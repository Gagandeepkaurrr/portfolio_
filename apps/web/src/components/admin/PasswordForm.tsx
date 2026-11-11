'use client';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useQueryClient } from '@tanstack/react-query';
import { useAdmin, OwnerSession } from '@/providers/AdminProvider';
import { jsonBody } from '@/lib/api/admin';
import { ErrorNotice, Notice } from './ui';
export function PasswordForm() {
  const { request } = useAdmin(); const client = useQueryClient(); const [error, setError] = useState<unknown>(null); const [success, setSuccess] = useState(false);
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<{ current_password: string; new_password: string }>();
  return <section className="admin-panel"><h2>Change your password</h2><p>Use a passphrase of 12–256 characters. Other sessions will be signed out.</p><ErrorNotice error={error} />{success && <Notice tone="success">Password changed. Your current session was renewed; other sessions were revoked.</Notice>}<form onSubmit={handleSubmit(async values => { setError(null); setSuccess(false); try { const session = await request<OwnerSession>('/admin/auth/change-password', { method: 'POST', body: jsonBody(values) }); if (session?.csrf_token) client.setQueryData(['owner-session'], session); else await client.invalidateQueries({ queryKey: ['owner-session'] }); reset(); setSuccess(true); } catch (problem) { setError(problem); } })}><div className="admin-form-grid"><div className="admin-field"><label htmlFor="current-password">Current password</label><input id="current-password" type="password" autoComplete="current-password" {...register('current_password', { required: 'Enter your current password.' })} />{errors.current_password && <small role="alert">{errors.current_password.message}</small>}</div><div className="admin-field"><label htmlFor="new-password">New passphrase</label><input id="new-password" type="password" autoComplete="new-password" {...register('new_password', { required: 'Enter a new passphrase.', minLength: { value: 12, message: 'Use at least 12 characters.' }, maxLength: { value: 256, message: 'Use no more than 256 characters.' } })} />{errors.new_password && <small role="alert">{errors.new_password.message}</small>}</div></div><button type="submit" className="admin-button" disabled={isSubmitting}>{isSubmitting ? 'Changing password…' : 'Change password'}</button></form></section>;
}
