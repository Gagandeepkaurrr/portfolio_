import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAppNavigation } from '@/lib/navigation';
import type { SiteContent } from '@/lib/types';
import { adminApi, ApiError, jsonBody } from '@/lib/api/admin';
import { changedSections } from '@/components/admin/draft-state';

export interface OwnerSession { owner: { id: string; email: string }; csrf_token: string; expires_at: string }
export interface ReleaseSummary { id: string; revision: number; published_at?: string; created_at?: string; source_draft_revision?: number }
export interface DraftEnvelope { revision: number; content: SiteContent; live_release: ReleaseSummary | null; updated_at?: string }
interface AdminContextValue {
  session: OwnerSession | null; sessionLoading: boolean; sessionError: unknown;
  draft: SiteContent | null; revision: number; liveRelease: ReleaseSummary | null;
  draftLoading: boolean; draftError: unknown; saveError: unknown; saving: boolean;
  dirtySections: string[]; conflict: boolean; requiresAuth: boolean;
  update: (updater: (value: SiteContent) => SiteContent) => void;
  save: () => Promise<void>; reload: () => Promise<void>; acceptDraft: (value: DraftEnvelope) => void;
  login: (email: string, password: string) => Promise<void>; logout: () => Promise<void>;
  request: <T>(path: string, options?: RequestInit) => Promise<T>;
  refreshStatus: () => Promise<void>;
}
const AdminContext = createContext<AdminContextValue | null>(null);
function OwnerState({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const router = useAppNavigation();
  const sessionQuery = useQuery({ queryKey: ['owner-session'], queryFn: () => adminApi<OwnerSession>('/admin/auth/session'), retry: false, staleTime: Infinity });
  const session = sessionQuery.data ?? null;
  const draftQuery = useQuery({ queryKey: ['owner-draft'], queryFn: () => adminApi<DraftEnvelope>('/admin/draft'), enabled: !!session, retry: false, staleTime: Infinity });
  const [draft, setDraft] = useState<SiteContent | null>(null);
  const [baseline, setBaseline] = useState<SiteContent | null>(null);
  const [revision, setRevision] = useState(0);
  const [liveRelease, setLiveRelease] = useState<ReleaseSummary | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<unknown>(null);
  const [conflict, setConflict] = useState(false);
  const [requiresAuth, setRequiresAuth] = useState(false);
  const lastRemote = useRef<DraftEnvelope | undefined>(undefined);
  const dirtySections = useMemo(() => draft && baseline ? changedSections(draft, baseline) : [], [draft, baseline]);
  const acceptDraft = useCallback((value: DraftEnvelope) => { setDraft(value.content); setBaseline(structuredClone(value.content)); setRevision(value.revision); setLiveRelease(value.live_release); setSaveError(null); setConflict(false); lastRemote.current = value; queryClient.setQueryData(['owner-draft'], value); }, [queryClient]);
  useEffect(() => {
    const remote = draftQuery.data;
    if (!remote || remote === lastRemote.current) return;
    lastRemote.current = remote;
    setLiveRelease(remote.live_release);
    if (dirtySections.length && remote.revision !== revision) { setConflict(true); return; }
    if (!draft || !dirtySections.length) acceptDraft(remote);
  }, [draftQuery.data, draft, dirtySections.length, revision, acceptDraft]);
  useEffect(() => {
    if (!dirtySections.length) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [dirtySections.length]);
  const request = useCallback(async <T,>(path: string, options: RequestInit = {}) => {
    try { return await adminApi<T>(path, { ...options, csrf: session?.csrf_token }); }
    catch (error) { if (error instanceof ApiError && error.status === 401) setRequiresAuth(true); throw error; }
  }, [session]);
  const save = async () => {
    if (!draft || saving) return;
    setSaving(true); setSaveError(null);
    const snapshot = structuredClone(draft);
    try {
      const saved = await request<DraftEnvelope>('/admin/draft', { method: 'PUT', headers: { 'If-Match': `"draft-${revision}"` }, body: jsonBody(snapshot) });
      setBaseline(structuredClone(saved.content)); setRevision(saved.revision); setLiveRelease(saved.live_release); setConflict(false);
      // Do not replace edits typed while the request was in flight.
      setDraft(current => current && changedSections(current, snapshot).length ? current : saved.content);
      lastRemote.current = saved; queryClient.setQueryData(['owner-draft'], saved);
    } catch (error) { setSaveError(error); if (error instanceof ApiError && error.status === 412) setConflict(true); throw error; }
    finally { setSaving(false); }
  };
  const reload = async () => { const remote = await request<DraftEnvelope>('/admin/draft'); acceptDraft(remote); };
  const login = async (email: string, password: string) => {
    const next = await adminApi<OwnerSession>('/admin/auth/login', { method: 'POST', body: jsonBody({ email, password }) });
    queryClient.setQueryData(['owner-session'], next); setRequiresAuth(false);
    await queryClient.invalidateQueries({ queryKey: ['owner-draft'] });
  };
  const logout = async () => {
    await request<void>('/admin/auth/logout', { method: 'POST' });
    setDraft(null); setBaseline(null); setRevision(0); setRequiresAuth(false);
    queryClient.clear(); router.replace('/admin/login');
  };
  const refreshStatus = async () => {
    const remote = await request<DraftEnvelope>('/admin/draft');
    setLiveRelease(remote.live_release);
    if (!dirtySections.length) acceptDraft(remote); else if (remote.revision !== revision) setConflict(true);
    await queryClient.invalidateQueries({ queryKey: ['releases'] });
  };
  return <AdminContext.Provider value={{ session, sessionLoading: sessionQuery.isPending, sessionError: sessionQuery.error, draft, revision, liveRelease, draftLoading: draftQuery.isPending, draftError: draftQuery.error, saveError, saving, dirtySections, conflict, requiresAuth, update: updater => setDraft(current => current ? updater(current) : current), save, reload, acceptDraft, login, logout, request, refreshStatus }}>{children}</AdminContext.Provider>;
}
export function AdminProvider({ children }: { children: ReactNode }) { const [client] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } })); return <QueryClientProvider client={client}><OwnerState>{children}</OwnerState></QueryClientProvider>; }
export function useAdmin() { const value = useContext(AdminContext); if (!value) throw new Error('Owner interface requires AdminProvider'); return value; }
