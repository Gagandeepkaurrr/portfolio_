'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AuthForm } from '@/components/admin/AuthForm';
export default function LoginPage() {
  const router = useRouter();
  return <main className="admin-login"><Link href="/" className="admin-login-brand">GK <span>Gagandeep Kaur</span></Link><section className="admin-login-card"><p className="admin-eyebrow">A personal journal of building</p><h1>Welcome to your studio.</h1><p>Make space for your next chapter. Sign in to edit, preview, and publish your portfolio.</p><AuthForm onSuccess={() => router.replace('/admin')} /><p className="admin-muted">This is the owner’s private workspace. If you need to reset your password, use the operator recovery command.</p></section><Link href="/">← Back to the portfolio</Link></main>;
}
