import base64
from contextlib import contextmanager
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
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

    def paired_source(self, source, *, server_version='0.1.0', archive_changes=None, extra=None):
        (source / 'server').mkdir(parents=True, exist_ok=True)
        (source / 'dist').mkdir(exist_ok=True)
        for key in ('dnd5e', 'dnd5e-server'):
            package = release.PACKAGES[key]
            manifest = {'id': package['id'], 'name': package['name'],
                        'version': server_version if key == 'dnd5e-server' else '0.1.0',
                        'sdk': {'requires': '>=1.0.0 <2.0.0'}}
            if key == 'dnd5e':
                manifest.update(system={'actorTypes': []}, entry='main.js',
                                content={'compendiums': ['compendiums/2014.json']})
            else:
                manifest['django'] = {'apps': ['gravewright_5e.apps.Gravewright5eConfig']}
            release.write(source / package['manifest'], manifest)
            archived = {**manifest, **((archive_changes or {}).get(key, {}))}
            with zipfile.ZipFile(source / 'dist' / f"{package['archive_prefix']}-{manifest['version']}.zip", 'w') as archive:
                archive.writestr('manifest.json', json.dumps(archived))
                if key == 'dnd5e':
                    archive.writestr('main.js', 'export default {};')
                    archive.writestr('compendiums/2014.json', json.dumps({'packs': [{'id': 'weapons', 'entries': []}]}))
                if extra:
                    archive.writestr(extra, 'unexpected')

    def repack(self, raw, *, changed=None, extra=None, mode=None):
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(raw)) as original, zipfile.ZipFile(output, 'w') as destination:
            for item in original.infolist():
                value = (changed or {}).get(item.filename, original.read(item))
                if mode is not None and item.filename == 'main.js':
                    item.external_attr = mode << 16
                destination.writestr(item, value, compress_type=zipfile.ZIP_DEFLATED)
            if extra:
                destination.writestr(extra, b'extra')
        return output.getvalue()

    @contextmanager
    def published_source(self, package, raw, *, tag_sha='a' * 40, draft=False, digest=None):
        filename = release.PACKAGES[package]['archive_prefix'] + '-0.1.0.zip'
        record = {'draft': draft, 'tag_name': 'v0.1.0', 'assets': [{
            'name': filename, 'state': 'uploaded', 'size': len(raw),
            'digest': digest or 'sha256:' + hashlib.sha256(raw).hexdigest(),
            'browser_download_url': 'https://github.com/Gravewright/dnd-srd-5e/releases/download/v0.1.0/' + filename,
        }]}

        def api(repository, path):
            self.assertEqual(repository, 'Gravewright/dnd-srd-5e')
            if path == 'git/ref/tags/v0.1.0':
                return {'object': {'type': 'commit', 'sha': tag_sha}}
            if path == 'releases/tags/v0.1.0':
                return record
            self.fail('Unexpected GitHub API path: ' + path)

        with patch.object(release, 'github_json', side_effect=api), \
                patch.object(release, 'download', return_value=raw) as download:
            yield download

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

    def test_paired_artifacts_publish_as_system_and_trusted_django_packages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.paired_source(root / 'source')
            for key, kind in [('dnd5e', 'system'), ('dnd5e-server', 'django')]:
                destination = root / key
                filename = release.PACKAGES[key]['archive_prefix'] + '-0.1.0.zip'
                built = (root / 'source/dist' / filename).read_bytes()
                public = self.repack(built)
                self.assertNotEqual(built, public)
                with self.published_source(key, public):
                    archive, record, tag = release.prepare(key, root / 'source', destination, 'a' * 40)
                self.assertEqual(list(destination.glob('*.zip')), [archive])
                self.assertEqual(archive.read_bytes(), public)
                self.assertEqual(record['sha256'], hashlib.sha256(public).hexdigest())
                self.assertEqual(record['type'], kind)
                self.assertEqual(record['name'], release.PACKAGES[key]['name'])
                self.assertEqual(tag, release.PACKAGES[key]['id'] + '-v0.1.0')
                self.assertNotIn('dependencies', record)

    def test_changed_source_release_payload_or_modes_are_rejected(self):
        for changes in [{'changed': {'main.js': b'adulterated'}}, {'mode': 0o100755},
                        {'extra': 'surprise.txt'}, {'extra': 'MAIN.JS'}]:
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.paired_source(root / 'source')
                built = (root / 'source/dist/gravewright-5e-srd-0.1.0.zip').read_bytes()
                with self.published_source('dnd5e', self.repack(built, **changes)):
                    with self.assertRaises(ValueError):
                        release.prepare('dnd5e', root / 'source', root / 'release', 'a' * 40)
                self.assertEqual(list((root / 'release').iterdir()), [])

    def test_source_release_requires_exact_tag_public_release_and_verified_digest(self):
        for changes in [{'tag_sha': 'b' * 40}, {'draft': True}, {'digest': 'sha256:' + '0' * 64}]:
            with self.subTest(changes=changes), self.published_source('dnd5e', b'archive', **changes):
                with self.assertRaises(ValueError):
                    release.source_release_archive('dnd5e', '0.1.0', 'gravewright-5e-srd-0.1.0.zip', 'a' * 40)

    def test_annotated_source_tag_is_resolved_to_approved_commit(self):
        raw = b'published archive'
        name = 'gravewright-5e-srd-0.1.0.zip'
        responses = [
            {'object': {'type': 'tag', 'sha': 'b' * 40}},
            {'object': {'type': 'commit', 'sha': 'a' * 40}},
            {'draft': False, 'tag_name': 'v0.1.0', 'assets': [{
                'name': name, 'state': 'uploaded', 'size': len(raw),
                'digest': 'sha256:' + hashlib.sha256(raw).hexdigest(),
                'browser_download_url': 'https://github.com/Gravewright/dnd-srd-5e/releases/download/v0.1.0/' + name,
            }]},
        ]
        with patch.object(release, 'github_json', side_effect=responses) as api, \
                patch.object(release, 'download', return_value=raw):
            self.assertEqual(release.source_release_archive('dnd5e', '0.1.0', name, 'a' * 40), raw)
        self.assertEqual(api.call_args_list[1].args[1], 'git/tags/' + 'b' * 40)

    def test_public_asset_download_never_receives_the_api_token(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.headers = {}
        response.read.return_value = b'archive'
        with patch.object(release, 'urlopen', return_value=response) as request, \
                patch.dict(release.os.environ, {'GH_TOKEN': 'temporary-test-token'}):
            release.download('https://github.com/Gravewright/dnd-srd-5e/releases/download/v0.1.0/test.zip', 64)
            self.assertIsNone(request.call_args.args[0].get_header('Authorization'))
            release.download('https://api.github.com/repos/Gravewright/dnd-srd-5e', 64, api=True)
            self.assertEqual(request.call_args.args[0].get_header('Authorization'), 'Bearer temporary-test-token')

    def test_mismatched_paired_versions_are_rejected_before_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.paired_source(root / 'source', server_version='0.1.1')
            with self.assertRaisesRegex(ValueError, 'versions must match'):
                release.prepare('dnd5e', root / 'source', root / 'release', 'a' * 40)

    def test_stale_manifest_unsafe_paths_and_duplicate_entries_are_rejected(self):
        for changes, extra in [({'dnd5e': {'description': 'stale archive'}}, None),
                               ({}, '../outside'), ({}, 'MAIN.JS')]:
            with self.subTest(changes=changes, extra=extra), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.paired_source(root / 'source', archive_changes=changes, extra=extra)
                with self.assertRaises(ValueError):
                    release.prepare('dnd5e', root / 'source', root / 'release', 'a' * 40)

    def test_manifest_cannot_disguise_trusted_server_as_browser_module(self):
        for key, change in [('dnd5e', {'system': None, 'django': {'apps': ['example']}}),
                            ('dnd5e-server', {'system': {}})]:
            package = release.PACKAGES[key]
            manifest = {'id': package['id'], 'name': package['name'], 'version': '0.1.0', **change}
            with self.subTest(package=key), self.assertRaises(ValueError):
                release.validate_manifest(package, manifest)

    def test_signed_display_fields_remain_compatible_with_host_ascii_contract(self):
        package = release.PACKAGES['dnd5e']
        manifest = {'id': package['id'], 'name': package['name'], 'version': '0.1.0',
                    'system': {}, 'description': 'Tradução'}
        with self.assertRaisesRegex(ValueError, 'ASCII'):
            release.validate_manifest(package, manifest)

    def test_failed_public_download_never_updates_catalog(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / 'release'
            directory.mkdir()
            self.archive(directory)
            _, record, _ = release.describe('dice3d', directory, 'a' * 40)
            key = Ed25519PrivateKey.generate()
            pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
            keys = {'test': base64.b64encode(key.public_key().public_bytes_raw()).decode()}
            signed = release.sign_record(record, pem, 'test', keys)
            release.write(directory / 'catalog.json', [signed])
            release.write(root / 'trusted-keys.json', keys)
            release.write(root / 'gravewright.marketplace.json', [])
            calls = []

            def run(command, **kwargs):
                calls.append(command)
                if command[:3] == ['gh', 'release', 'download']:
                    destination = Path(command[command.index('--dir') + 1])
                    (destination / 'dice.zip').write_bytes(b'wrong bytes')

            args = ['release.py', 'publish', '--package', 'dice3d', '--directory', str(directory),
                    '--source-sha', 'a' * 40]
            with patch.object(release, 'ROOT', root), patch.object(release.subprocess, 'run', side_effect=run), \
                    patch('sys.argv', args), patch.dict(release.os.environ, {'GITHUB_SHA': 'b' * 40}):
                with self.assertRaisesRegex(ValueError, 'differs from the approved archive'):
                    release.main()
            self.assertEqual(release.read(root / 'gravewright.marketplace.json'), [])
            self.assertFalse(any(command[0] == 'git' for command in calls))
            publish = next(command for command in calls if command[:3] == ['gh', 'release', 'edit'])
            self.assertEqual(publish[publish.index('--tag') + 1], 'gravewright-3d-dice-v0.1.1')
            self.assertEqual(publish[publish.index('--target') + 1], 'b' * 40)


if __name__ == '__main__':
    unittest.main()
