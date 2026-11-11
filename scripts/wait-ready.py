#!/usr/bin/env python3
"""Bounded readiness polling for actual services; no blind startup sleep."""
import sys
import time
import urllib.error
import urllib.request

pending = set(sys.argv[1:])
if not pending:
    raise SystemExit('Usage: wait-ready.py URL [URL ...]')
deadline = time.monotonic() + 90
while pending and time.monotonic() < deadline:
    for url in list(pending):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if 200 <= response.status < 300:
                    pending.remove(url)
        except (OSError, urllib.error.HTTPError):
            pass
    if pending:
        time.sleep(0.5)
if pending:
    raise SystemExit('Timed out waiting for: ' + ', '.join(sorted(pending)))
print('All requested services are ready.')
