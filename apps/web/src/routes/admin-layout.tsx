import { Outlet } from 'react-router';
import { AdminProvider } from '@/providers/AdminProvider';
import '@/styles/admin.css';
export const meta = () => [{ title: 'Owner studio · Gagandeep Kaur' }, { name: 'robots', content: 'noindex, nofollow' }];
export default function AdminLayout() { return <AdminProvider><Outlet /></AdminProvider>; }
