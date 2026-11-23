import os
import re
import uuid
from pathlib import Path
from app.config import get_settings


class LocalStorage:
    def __init__(self):
        self.root = get_settings().media_root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def path(self, key: str) -> Path:
        if not re.fullmatch(r'[a-f0-9]{32}', key):
            raise ValueError('Invalid internal storage key')
        return self.root / key

    def write_private(self, data: bytes) -> str:
        key = uuid.uuid4().hex
        path = self.path(key)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return key

    def read_private(self, key: str) -> bytes:
        return self.path(key).read_bytes()

    def stat(self, key: str):
        return self.path(key).stat()

    def delete(self, key: str):
        self.path(key).unlink(missing_ok=True)

    def health_check(self):
        key = self.write_private(b'health')
        self.delete(key)
        return True
