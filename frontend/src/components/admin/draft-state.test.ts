import { describe, expect, it } from 'vitest';
import { acceptRemote, changedSections, makePublishRequest, switchNarrativeFormat } from './draft-state';

describe('owner draft conflict handling', () => {
  it('keeps unsaved content when a newer remote revision arrives', () => {
    const baseline = { profile: { full_name: 'Gagandeep' }, projects: [] };
    const local = { ...baseline, profile: { full_name: 'Unsaved edit' } };
    const remote = { ...baseline, profile: { full_name: 'Other editor' } };
    expect(acceptRemote(local, baseline, remote)).toEqual({ content: local, conflict: true });
  });
  it('accepts fresh remote content when local edits are clean', () => {
    const baseline = { profile: { full_name: 'Gagandeep' } };
    const remote = { profile: { full_name: 'Updated profile' } };
    expect(acceptRemote(baseline, baseline, remote)).toEqual({ content: remote, conflict: false });
  });
  it('identifies changed sections without treating object key order as edits', () => {
    expect(changedSections({ profile: { name: 'A', role: 'B' }, projects: [] }, { projects: [], profile: { role: 'B', name: 'A' } })).toEqual([]);
    expect(changedSections({ profile: { name: 'A' }, projects: [] }, { profile: { name: 'B' }, projects: [] })).toEqual(['profile']);
  });
  it('binds an idempotent publication to the reviewed draft and live release', () => {
    expect(makePublishRequest(12, 'release-one', 'request-one')).toEqual({ expected_draft_revision: 12, expected_live_release_id: 'release-one', idempotency_key: 'request-one' });
  });
});

it('switches authored paragraphs to bullets without losing text or retaining an invalid mixed payload', () => {
  expect(switchNarrativeFormat({ id: 'story', kind: 'paragraph', text: 'My actual lesson.', items: [] }, 'bullet_list')).toEqual({ id: 'story', kind: 'bullet_list', text: null, items: ['My actual lesson.'] });
  expect(switchNarrativeFormat({ id: 'story', kind: 'bullet_list', text: null, items: ['First lesson.', 'Second lesson.'] }, 'paragraph')).toEqual({ id: 'story', kind: 'paragraph', text: 'First lesson.\nSecond lesson.', items: [] });
});
