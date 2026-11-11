import { useMemo } from 'react';
import { useNavigate } from 'react-router';

/** Stable navigation actions keep existing owner effects independent of renders. */
export function useAppNavigation() {
  const navigate = useNavigate();
  return useMemo(() => ({
    push: (to: string) => { void navigate(to); },
    replace: (to: string) => { void navigate(to, { replace: true }); },
  }), [navigate]);
}
