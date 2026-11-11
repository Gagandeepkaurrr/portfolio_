export function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, val]) => `${JSON.stringify(key)}:${canonical(val)}`).join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}
export function changedSections<T extends object>(current: T, baseline: T): string[] {
  return [...new Set([...Object.keys(current), ...Object.keys(baseline)])].filter(key => canonical((current as Record<string, unknown>)[key]) !== canonical((baseline as Record<string, unknown>)[key]));
}
export function acceptRemote<T extends object>(current: T, baseline: T, remote: T): { content: T; conflict: boolean } {
  const dirty = changedSections(current, baseline).length > 0;
  return { content: dirty ? current : remote, conflict: dirty };
}
export function makePublishRequest(revision: number, liveId: string | null, key: string) {
  return { expected_draft_revision: revision, expected_live_release_id: liveId, idempotency_key: key };
}
export function switchNarrativeFormat(block: import('@/lib/types').NarrativeBlock, kind: 'paragraph' | 'bullet_list'): import('@/lib/types').NarrativeBlock {
  if (kind === block.kind) return block;
  return kind === 'paragraph'
    ? { ...block, kind, text: (block.items ?? []).join('\n'), items: [] }
    : { ...block, kind, text: null, items: block.text ? [block.text] : [] };
}
