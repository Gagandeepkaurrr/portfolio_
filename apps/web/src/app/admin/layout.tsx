import type { Metadata } from 'next';
import { AdminProvider } from '@/providers/AdminProvider';
import '@/styles/admin.css';
export const dynamic = 'force-dynamic';
export const metadata: Metadata = { title: 'Owner studio · Gagandeep Kaur', robots: { index: false, follow: false } };
export default function AdminLayout({ children }: { children: React.ReactNode }) { return <AdminProvider>{children}</AdminProvider>; }
