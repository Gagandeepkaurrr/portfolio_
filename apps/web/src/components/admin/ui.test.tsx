import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from './ui';
function NavigationDialog() {
  const [open, setOpen] = useState(false);
  return <><button onClick={() => setOpen(true)}>Open studio navigation</button><Modal open={open} onOpenChange={setOpen} title="Owner studio" description="Choose an area to edit."><button type="button">Profile</button></Modal></>;
}
describe('owner dialog keyboard navigation', () => {
  it('restores focus to the opener after Escape closes the dialog', async () => {
    const user = userEvent.setup();
    render(<NavigationDialog />);
    const opener = screen.getByRole('button', { name: 'Open studio navigation' });
    await user.click(opener);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(opener).toHaveFocus();
  });
});
