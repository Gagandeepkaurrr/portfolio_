import importlib.util
import io
import json
import subprocess
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from backup_common import safe_media_extract, validate_restore_name, media_hashes

class BackupSafetyTests(unittest.TestCase):
    def test_refuses_traversal_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for mode in ('traversal', 'symlink'):
                archive = root / f'{mode}.tar.gz'
                with tarfile.open(archive, 'w:gz') as bundle:
                    info = tarfile.TarInfo('../outside' if mode == 'traversal' else 'link')
                    if mode == 'symlink':
                        info.type = tarfile.SYMTYPE
                        info.linkname = '/etc/passwd'
                        bundle.addfile(info)
                    else:
                        info.size = 4
                        bundle.addfile(info, io.BytesIO(b'evil'))
                with self.assertRaises(ValueError):
                    safe_media_extract(archive, root / 'output')
            self.assertFalse((root.parent / 'outside').exists())

    def test_requires_disposable_target_name(self):
        for value in ('', 'production', 'portfolio', 'portfolio-restore-../test', 'portfolio-restore-'):
            with self.assertRaises(ValueError):
                validate_restore_name(value)
        self.assertEqual(validate_restore_name('portfolio-restore-rehearsal-123'), 'portfolio-restore-rehearsal-123')

    def test_corrupted_backup_is_rejected_before_target_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'database.dump').write_bytes(b'changed')
            (root/'media.tar.gz').write_bytes(b'unused')
            (root/'manifest.json').write_text(json.dumps({'format':1,'database_sha256':'0'*64,'archive_sha256':'0'*64}))
            script = Path(__file__).resolve().parents[2]/'scripts/restore.py'
            result = subprocess.run([sys.executable,str(script),'--backup',str(root),'--name','portfolio-restore-corrupt-test'],text=True,capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Checksum mismatch', result.stderr)

    def test_media_hashes_detect_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'nested').mkdir()
            path = root/'nested/image.webp'
            path.write_bytes(b'first')
            before = media_hashes(root)
            path.write_bytes(b'second')
            self.assertNotEqual(before, media_hashes(root))
            self.assertEqual(list(before), ['nested/image.webp'])

if __name__ == '__main__':
    unittest.main()
