#!/usr/bin/env python3
"""Create private, non-overwriting local configuration; never print secrets."""
from pathlib import Path
import os
import secrets

root = Path(__file__).resolve().parents[1]
env_file = root / '.env'
if env_file.exists():
    print('.env already exists; preserved unchanged.')
    raise SystemExit(0)
password = secrets.token_hex(24)
text = (root / '.env.example').read_text()
text = text.replace('REPLACE_WITH_RANDOM_VALUE', password)
text = text.replace('REPLACE_WITH_AT_LEAST_32_RANDOM_BYTES', secrets.token_hex(32))
text = text.replace('REPLACE_WITH_SEPARATE_RANDOM_SECRET', secrets.token_hex(32))
text = text.replace('MEDIA_ROOT=.data/media', f'MEDIA_ROOT={root}/.data/media')
fd = os.open(env_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
with os.fdopen(fd, 'w') as stream:
    stream.write(text)
(root / '.data' / 'media').mkdir(parents=True, exist_ok=True)
print('Created private .env for localhost development. No owner account was created.')
