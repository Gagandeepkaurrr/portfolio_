import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAdmin } from '@/providers/AdminProvider';
import { ErrorNotice } from './ui';
const schema = z.object({ email: z.string().email('Enter a valid email address.'), password: z.string().min(1, 'Enter your password.') });
export function AuthForm({ onSuccess, reauth = false }: { onSuccess?: () => void; reauth?: boolean }) {
  const { login } = useAdmin();
  const [error, setError] = useState<unknown>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<z.infer<typeof schema>>({ resolver: zodResolver(schema) });
  return <form className="admin-auth-form" onSubmit={handleSubmit(async values => { setError(null); try { await login(values.email, values.password); onSuccess?.(); } catch (problem) { setError(problem); } })}>
    <ErrorNotice error={error} />
    <div className="admin-field"><label htmlFor={reauth ? 'reauth-email' : 'login-email'}>Email address</label><input id={reauth ? 'reauth-email' : 'login-email'} type="email" autoComplete="username" {...register('email')} aria-invalid={!!errors.email} aria-describedby={errors.email ? 'auth-email-error' : undefined} />{errors.email && <small id="auth-email-error" role="alert">{errors.email.message}</small>}</div>
    <div className="admin-field"><label htmlFor={reauth ? 'reauth-password' : 'login-password'}>Password</label><input id={reauth ? 'reauth-password' : 'login-password'} type="password" autoComplete="current-password" {...register('password')} aria-invalid={!!errors.password} aria-describedby={errors.password ? 'auth-password-error' : undefined} />{errors.password && <small id="auth-password-error" role="alert">{errors.password.message}</small>}</div>
    <button className="admin-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Signing in…' : reauth ? 'Sign in and continue editing' : 'Sign in'}</button>
  </form>;
}
