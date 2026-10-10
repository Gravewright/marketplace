import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

spec = importlib.util.spec_from_file_location('release', Path(__file__).resolve().parents[1] / 'scripts/release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def archive(self, directory, **changes):
        manifest = {'id': 'gravewright-3d-dice', 'name': 'Dice', 'version': '0.1.1',
                    'sdk': {'requires': '>=1.0.0 <2.0.0'}}
        manifest.update(changes)
        with zipfile.ZipFile(directory / 'dice.zip', 'w') as archive:
            archive.writestr('manifest.json', json.dumps(manifest))

    def test_record_is_bound_to_archive_version_and_central_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.archive(directory)
            _, record, tag = release.describe('dice3d', directory, 'a' * 40)
            self.assertEqual(tag, 'gravewright-3d-dice-v0.1.1')
            self.assertEqual(record['download'],
                             'https://github.com/Gravewright/marketplace/releases/download/' + tag + '/dice.zip')
            self.assertEqual(len(record['sha256']), 64)

    def test_wrong_package_version_source_or_multiple_archives_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for changes in ({'id': 'another-module'}, {'version': '../oops'}):
                self.archive(directory, **changes)
                with self.assertRaises(ValueError):
                    release.describe('dice3d', directory, 'a' * 40)
            self.archive(directory)
            with self.assertRaises(ValueError):
                release.describe('dice3d', directory, 'main')
            (directory / 'extra.zip').write_bytes(b'archive')
            with self.assertRaises(ValueError):
                release.describe('dice3d', directory, 'a' * 40)

    def test_signature_matches_host_canonicalization_and_preserves_old_keys(self):
        key = Ed25519PrivateKey.generate()
        keys = {'new': base64.b64encode(key.public_key().public_bytes_raw()).decode(), 'old': 'unchanged'}
        pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        record = {'id': 'test', 'tags': ['Tradução'], 'version': '1.0.0'}
        signed = release.sign_record(record, pem, 'new', keys)
        canonical = json.dumps({k: v for k, v in signed.items() if k != 'signature'}, sort_keys=True,
                               separators=(',', ':'), ensure_ascii=True).encode('ascii')
        key.public_key().verify(base64.b64decode(signed['signature']), canonical)
        self.assertEqual(keys['old'], 'unchanged')
        with self.assertRaises(ValueError):
            release.sign_record(record, pem, 'old', keys)


if __name__ == '__main__':
    unittest.main()
