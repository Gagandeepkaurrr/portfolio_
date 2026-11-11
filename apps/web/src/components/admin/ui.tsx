'use client';
import * as Dialog from '@radix-ui/react-dialog';
import { ReactNode, useEffect, useId, useRef } from 'react';
import { ApiError } from '@/lib/api/admin';

export function Notice({ children, tone = 'info' }: { children: ReactNode; tone?: 'info' | 'error' | 'success' }) {
  return <div className={`admin-notice ${tone}`} role={tone === 'error' ? 'alert' : 'status'}>{children}</div>;
}
export function ErrorNotice({ error }: { error: unknown }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { if (error) ref.current?.focus(); }, [error]);
  if (!error) return null;
  const value = error instanceof Error ? error.message : 'Something went wrong. Please try again.';
  return <div ref={ref} tabIndex={-1} className="admin-notice error" role="alert"><p>{value}</p>{error instanceof ApiError && error.fieldErrors.length > 0 && <ul>{error.fieldErrors.map((item, index) => <li key={index}><strong>{Array.isArray(item.path) ? item.path.join(' › ') : item.path}</strong>: {item.message}</li>)}</ul>}{error instanceof ApiError && error.requestId && <small>Reference: {error.requestId}</small>}</div>;
}
export function Field({ label, value, onChange, type = 'text', multiline = false, help, required, maxLength, placeholder, min, max, step }: { label: string; value: string | number | null | undefined; onChange: (value: string) => void; type?: string; multiline?: boolean; help?: string; required?: boolean; maxLength?: number; placeholder?: string; min?: number; max?: number; step?: number }) {
  const id = useId();
  const props = { id, value: value ?? '', onChange: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(event.target.value), required, maxLength, placeholder, 'aria-describedby': help ? `${id}-help` : undefined };
  return <div className={`admin-field${multiline ? ' wide' : ''}`}><label htmlFor={id}>{label}{required && <span aria-hidden="true"> *</span>}</label>{multiline ? <textarea {...props} rows={4} /> : <input {...props} type={type} min={min} max={max} step={step} />}{help && <small id={`${id}-help`}>{help}</small>}</div>;
}
export function Toggle({ label, checked, onChange, help }: { label: string; checked: boolean; onChange: (checked: boolean) => void; help?: string }) {
  const id = useId();
  return <div className="admin-toggle"><label htmlFor={id}><input id={id} type="checkbox" checked={checked} onChange={event => onChange(event.target.checked)} /> <span>{label}</span></label>{help && <small>{help}</small>}</div>;
}
const dialogReturnTargets = new WeakMap<Element, HTMLElement>();
export function Modal({ open, onOpenChange, title, description, children }: { open: boolean; onOpenChange: (value: boolean) => void; title: string; description?: string; children: ReactNode }) {
  const contentRef = useRef<HTMLDivElement>(null);
  const returnFocus = useRef<HTMLElement | null>(null);
  return <Dialog.Root open={open} onOpenChange={onOpenChange}><Dialog.Portal><Dialog.Overlay className="admin-dialog-overlay" /><Dialog.Content ref={contentRef} className="admin-dialog" onOpenAutoFocus={() => {
    const active = document.activeElement;
    if (active instanceof HTMLElement) {
      const parentDialog = active.closest('[role="dialog"]');
      returnFocus.current = parentDialog ? dialogReturnTargets.get(parentDialog) ?? active : active;
      if (contentRef.current && returnFocus.current) dialogReturnTargets.set(contentRef.current, returnFocus.current);
    }
  }} onCloseAutoFocus={event => {
    event.preventDefault();
    if (!document.querySelector('[role="dialog"][data-state="open"]') && returnFocus.current?.isConnected) returnFocus.current.focus();
  }}><Dialog.Title>{title}</Dialog.Title>{description && <Dialog.Description>{description}</Dialog.Description>}<Dialog.Close className="admin-dialog-close" aria-label="Close dialog">×</Dialog.Close>{children}</Dialog.Content></Dialog.Portal></Dialog.Root>;
}
export function Confirm({ open, onOpenChange, title, description, label, pending, error, onConfirm }: { open: boolean; onOpenChange: (value: boolean) => void; title: string; description: string; label: string; pending?: boolean; error?: unknown; onConfirm: () => void }) {
  return <Modal open={open} onOpenChange={onOpenChange} title={title} description={description}><ErrorNotice error={error} /><div className="admin-actions"><button type="button" className="admin-button secondary" onClick={() => onOpenChange(false)}>Cancel</button><button type="button" className="admin-button danger" disabled={pending} onClick={onConfirm}>{pending ? 'Working…' : label}</button></div></Modal>;
}
export function ListEditor({ label, items, onChange, max = 30 }: { label: string; items: string[]; onChange: (items: string[]) => void; max?: number }) {
  return <fieldset className="admin-list-field"><legend>{label}</legend>{items.map((item, index) => <div className="admin-list-row" key={index}><input aria-label={`${label} ${index + 1}`} value={item} onChange={event => onChange(items.map((value, i) => i === index ? event.target.value : value))} /><button type="button" className="admin-icon-button" disabled={index === 0} aria-label={`Move ${label} ${index + 1} up`} onClick={() => { const next = [...items]; [next[index - 1], next[index]] = [next[index], next[index - 1]]; onChange(next); }}>↑</button><button type="button" className="admin-icon-button" disabled={index === items.length - 1} aria-label={`Move ${label} ${index + 1} down`} onClick={() => { const next = [...items]; [next[index + 1], next[index]] = [next[index], next[index + 1]]; onChange(next); }}>↓</button><button type="button" className="admin-icon-button" aria-label={`Remove ${label} ${index + 1}`} onClick={() => onChange(items.filter((_, i) => i !== index))}>×</button></div>)}<button type="button" className="admin-button secondary small" disabled={items.length >= max} onClick={() => onChange([...items, ''])}>+ Add {label.toLowerCase().replace(/s$/, '')}</button></fieldset>;
}
