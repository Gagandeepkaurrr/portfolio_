'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { PublicProject, PublicSiteContent } from '@/lib/types';
import { useAdmin } from '@/providers/AdminProvider';
import { PortfolioHome, ProjectDetail, PublicShell } from '@/components/public';
import { ErrorNotice, Notice } from './ui';
interface PreviewContent { draft_revision: number; content: PublicSiteContent; validation_warnings: unknown[] }
interface ProjectPreview { draft_revision: number; project: PublicProject; is_hidden: boolean; validation_warnings: unknown[] }
function usePreview(projectId?: string) {
  const { request, revision } = useAdmin();
  const site = useQuery({ queryKey: ['preview', revision], queryFn: () => request<PreviewContent>('/admin/preview') });
  const project = useQuery({ queryKey: ['project-preview', projectId, revision], queryFn: () => request<ProjectPreview>(`/admin/preview/projects/${projectId}`), enabled: !!projectId });
  return { site, project };
}
export function PreviewFrame({ projectId }: { projectId?: string }) {
  const { site, project } = usePreview(projectId);
  useEffect(() => {
    const sendSize = () => window.parent.postMessage({ type: 'portfolio-preview-height', height: document.documentElement.scrollHeight }, window.location.origin);
    const observer = new ResizeObserver(sendSize); observer.observe(document.body); sendSize();
    return () => observer.disconnect();
  }, []);
  return <div className="admin-preview-frame" onClickCapture={event => {
    const target = event.target instanceof Element ? event.target.closest('a') : null;
    if (!target || target.target === '_blank') return;
    const url = new URL(target.href, window.location.origin);
    if (url.origin !== window.location.origin) return;
    const linkedProject = site.data?.content.projects.find(item => url.pathname === `/projects/${item.slug}`);
    if (linkedProject) { event.preventDefault(); event.stopPropagation(); window.parent.postMessage({ type: 'portfolio-preview-project', id: linkedProject.id }, window.location.origin); }
    else if (url.pathname === '/') { event.preventDefault(); event.stopPropagation(); if (!projectId) document.getElementById(url.hash.slice(1) || 'top')?.scrollIntoView(); else window.parent.postMessage({ type: 'portfolio-preview-home', hash: url.hash }, window.location.origin); }
  }}><ErrorNotice error={site.error ?? project.error} />{site.isPending || (projectId && project.isPending) ? <p role="status">Rendering saved draft…</p> : site.data && <PublicShell content={site.data.content}>{projectId && project.data ? <ProjectDetail project={project.data.project} projects={site.data.content.projects} /> : <PortfolioHome content={site.data.content} />}</PublicShell>}</div>;
}
export function Preview({ projectId }: { projectId?: string }) {
  const { revision, dirtySections } = useAdmin(); const router = useRouter(); const [anchor, setAnchor] = useState(''); const [mobile, setMobile] = useState(false); const [height, setHeight] = useState(900); const frame = useRef<HTMLIFrameElement>(null);
  const { site, project } = usePreview(projectId);
  useEffect(() => { const receive = (event: MessageEvent) => {
    if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return;
    if (event.data?.type === 'portfolio-preview-height') { const value = Number(event.data.height); if (Number.isFinite(value)) setHeight(Math.max(500, Math.min(40000, value))); }
    if (event.data?.type === 'portfolio-preview-project' && /^[a-f0-9-]{36}$/i.test(event.data.id)) { setAnchor(''); router.push(`/admin/preview/projects/${event.data.id}`); }
    if (event.data?.type === 'portfolio-preview-home') { setAnchor(/^#[a-z]+$/.test(event.data.hash) ? event.data.hash : ''); router.push('/admin/preview'); }
  }; window.addEventListener('message', receive); return () => window.removeEventListener('message', receive); }, [router]);
  const warnings = projectId ? project.data?.validation_warnings : site.data?.validation_warnings;
  const src = `/admin/preview/frame${projectId ? `/projects/${projectId}` : ''}?revision=${revision}${anchor}`;
  return <><div className="admin-preview-banner"><div><strong>{project.data?.is_hidden ? 'Hidden project preview' : 'Draft preview'}</strong><span>Saved revision {site.data?.draft_revision ?? revision} · visible only to you</span></div><div className="admin-actions"><button className="admin-button secondary small" aria-pressed={!mobile} onClick={() => setMobile(false)}>Desktop</button><button className="admin-button secondary small" aria-pressed={mobile} onClick={() => setMobile(true)}>Mobile</button><Link className="admin-button small" href={projectId ? `/admin/content/projects/${projectId}` : '/admin'}>Return to editor</Link></div></div>{dirtySections.length > 0 && <Notice>Your unsaved edits are not shown here. Save your draft to preview them.</Notice>}{warnings && warnings.length > 0 && <Notice tone="error"><strong>Draft needs attention before publication.</strong><ul>{warnings.map((item, index) => <li key={index}>{typeof item === 'string' ? item : item && typeof item === 'object' && 'message' in item ? String(item.message) : JSON.stringify(item)}</li>)}</ul></Notice>}<ErrorNotice error={site.error ?? project.error} />{site.isPending || (projectId && project.isPending) ? <p role="status">Rendering your saved draft…</p> : site.data && <div className={`admin-preview-canvas ${mobile ? 'mobile' : ''}`}><iframe key={src} ref={frame} title={projectId ? 'Saved project draft preview' : 'Saved home page draft preview'} src={src} style={{ height }} /></div>}</>;
}
