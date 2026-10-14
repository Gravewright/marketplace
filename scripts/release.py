"""Sign approved archives and publish them from the central Marketplace repo."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
from urllib.request import Request, urlopen
import zipfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    'dice3d': {'id': 'gravewright-3d-dice', 'repo': 'Gravewright/Gravewright-3D-Dice',
               'tags': ['Dados', '3D', 'Rolagens']},
    'translator': {'id': 'gravewright.translator', 'repo': 'Gravewright/translator',
                   'tags': ['Tradução', 'Idiomas', 'Interface']},
    'dnd5e': {'id': 'gravewright.5e-srd', 'repo': 'Gravewright/dnd-srd-5e',
              'name': 'DnD 5e SRD', 'type': 'system', 'manifest': 'manifest.json',
              'archive_prefix': 'gravewright-5e-srd', 'tags': ['D&D', '5e', 'SRD', '2014', '2024']},
    'dnd5e-server': {'id': 'gravewright.5e-srd-server', 'repo': 'Gravewright/dnd-srd-5e',
                     'name': 'DnD 5e SRD - Server Rules', 'type': 'django',
                     'manifest': 'server/manifest.json', 'archive_prefix': 'gravewright-5e-srd-server',
                     'tags': ['D&D', '5e', 'SRD', 'Automações', 'Servidor']},
    'swade': {'id': 'gravewright.savage-worlds',
              'repo': 'Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright',
              'name': 'Savage Worlds Compatibility Package for Gravewright',
              'type': 'system', 'manifest': 'manifest.json',
              'archive_prefix': 'gravewright-savage-worlds',
              'catalog_description': 'Original editable SWADE sheets, item templates and package-owned automation, without game content or compendiums. Requires the matching server companion and Gravewright VTT 0.2.3+ with context.host and card.asset.upload support. English by default; optional official Translator for Portuguese and Spanish.',
              'tags': ['Savage Worlds', 'SWADE', 'Fichas', 'Automação']},
    'swade-server': {'id': 'gravewright.savage-worlds.rules',
                     'repo': 'Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright',
                     'name': 'Savage Worlds Compatibility Package for Gravewright — Server Rules',
                     # The host's signed catalog contract permits ASCII display fields.
                     # The package manifest retains the approved public display name.
                     'catalog_name': 'Savage Worlds Compatibility Package for Gravewright - Server Rules',
                     'type': 'django', 'manifest': 'server/manifest.json',
                     'archive_prefix': 'gravewright-savage-worlds-rules',
                     'catalog_description': 'Trusted server companion for configured Savage Worlds effect, power and turn clocks. Requires the browser package of the same version and Gravewright VTT 0.2.3+ with context.host and card.asset.upload support. Activate as host owner through the managed Runner. Contains no catalogs or game content.',
                     'tags': ['Savage Worlds', 'SWADE', 'Automação', 'Servidor']},
}
PAIRED_PACKAGES = (('dnd5e', 'dnd5e-server'), ('swade', 'swade-server'))
SAVAGE_NOTICE = ('This game references the Savage Worlds game system, available from '
                 'Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all '
                 'associated logos and trademarks are copyrights of Pinnacle Entertainment '
                 'Group. Used with permission. Pinnacle makes no representation or warranty '
                 'as to the quality, viability, or suitability for purpose of this product.')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


def validate_manifest(package, manifest):
    if (manifest.get('id') != package['id']
            or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', manifest.get('version', ''))):
        raise ValueError('Unexpected module ID or invalid stable version.')
    if 'system' in manifest and 'django' in manifest:
        raise ValueError('A package cannot contain both a browser system and a Django app.')
    kind = 'django' if 'django' in manifest else 'system' if 'system' in manifest else 'module'
    if kind != package.get('type', 'module'):
        raise ValueError('Manifest kind does not match the approved package type.')
    if package.get('name') and manifest.get('name') != package['name']:
        raise ValueError('Unexpected package display name.')
    for field in ('name', 'description'):
        value = package.get('catalog_' + field, manifest.get(field, manifest.get('name', '')))
        if not isinstance(value, str) or not value or not value.isascii():
            raise ValueError('Signed display fields must be nonempty ASCII strings.')


def download(url, limit, *, api=False):
    headers = {'User-Agent': 'Gravewright-Marketplace-Publisher'}
    if api:
        headers.update(Accept='application/vnd.github+json', **{'X-GitHub-Api-Version': '2022-11-28'})
        if os.environ.get('GH_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    # Public release downloads deliberately receive no token, including redirects.
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        if int(response.headers.get('Content-Length', '0')) > limit:
            raise ValueError('Source release download exceeds its byte quota.')
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Source release download exceeds its byte quota.')
    return raw


def github_json(repository, path):
    return json.loads(download(f'https://api.github.com/repos/{repository}/{path}', 2 * 1024 * 1024, api=True))


def source_release_archive(package, version, filename, source_sha):
    """Require a public source release tied to the exact tested Git commit."""
    repository = PACKAGES[package]['repo']
    tag = 'v' + version
    target = github_json(repository, 'git/ref/tags/' + tag)['object']
    for _ in range(5):
        if target.get('type') != 'tag':
            break
        if not re.fullmatch('[0-9a-f]{40}', target.get('sha', '')):
            raise ValueError('Invalid source Git tag object.')
        target = github_json(repository, 'git/tags/' + target['sha'])['object']
    if target.get('type') != 'commit' or target.get('sha') != source_sha:
        raise ValueError('The source release tag does not identify the tested commit.')
    release = github_json(repository, 'releases/tags/' + tag)
    if release.get('draft') is not False or release.get('tag_name') != tag:
        raise ValueError('A published source release with the expected version is required.')
    assets = [item for item in release.get('assets', []) if item.get('name') == filename]
    if len(assets) != 1:
        raise ValueError('Expected one published source release asset with the selected filename.')
    asset = assets[0]
    expected_url = f'https://github.com/{repository}/releases/download/{tag}/{filename}'
    if (asset.get('state') != 'uploaded' or asset.get('browser_download_url') != expected_url
            or type(asset.get('size')) is not int or not 0 < asset['size'] <= 64 * 1024 * 1024
            or not re.fullmatch('sha256:[0-9a-f]{64}', asset.get('digest') or '')):
        raise ValueError('Invalid source release asset URL, size or SHA-256 metadata.')
    raw = download(expected_url, 64 * 1024 * 1024)
    if len(raw) != asset['size'] or 'sha256:' + hashlib.sha256(raw).hexdigest() != asset['digest']:
        raise ValueError('Source release asset size or digest does not match the GitHub metadata.')
    return raw


def archive_payload(raw):
    """Read bounded, safe entries; compare payload and modes across compressors."""
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError('The archive exceeds the host package quota.')
    with zipfile.ZipFile(io.BytesIO(raw)) as contents:
        entries = contents.infolist()
        if not entries or len(entries) > 4096 or sum(item.file_size for item in entries) > 256 * 1024 * 1024:
            raise ValueError('The expanded archive exceeds the host package quota.')
        names, payload = set(), {}
        for item in entries:
            name = item.filename.rstrip('/')
            mode = item.external_attr >> 16
            if (not name or name.startswith('/') or '\\' in name or ':' in name
                    or any(part in {'', '.', '..'} for part in name.split('/'))
                    or name.casefold() in names or item.flag_bits & 1
                    or stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}):
                raise ValueError('Unsafe or duplicate archive entry.')
            names.add(name.casefold())
            payload[item.filename] = (mode, item.is_dir(), contents.read(item))
        return payload


def prepare(package, source, directory, source_sha):
    """Select one tested paired artifact, preserving the one-ZIP signing boundary."""
    pair = next((group for group in PAIRED_PACKAGES if package in group), None)
    if pair is None:
        raise ValueError('Artifact selection is only needed for paired system packages.')
    if not re.fullmatch('[0-9a-f]{40}', source_sha):
        raise ValueError('A full source commit SHA is required.')
    manifests = {key: read(source / PACKAGES[key]['manifest'])
                 for key in pair}
    for key, manifest in manifests.items():
        validate_manifest(PACKAGES[key], manifest)
    if manifests[pair[0]]['version'] != manifests[pair[1]]['version']:
        raise ValueError('Browser and server package versions must match.')
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('The artifact destination must be empty.')
    directory.mkdir(parents=True, exist_ok=True)
    expected = manifests[package]
    filename = f"{PACKAGES[package]['archive_prefix']}-{expected['version']}.zip"
    archive = source / 'dist' / filename
    if archive.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('The archive exceeds the host package quota.')
    with zipfile.ZipFile(archive) as contents:
        if len(contents.infolist()) > 4096 or sum(item.file_size for item in contents.infolist()) > 256 * 1024 * 1024:
            raise ValueError('The expanded archive exceeds the host package quota.')
        names = set()
        for item in contents.infolist():
            name = item.filename.rstrip('/')
            mode = item.external_attr >> 16
            if (not name or name.startswith('/') or '\\' in name or ':' in name
                    or any(part in {'', '.', '..'} for part in name.split('/'))
                    or name.casefold() in names or item.flag_bits & 1
                    or stat.S_ISLNK(mode)):
                raise ValueError('Unsafe or duplicate archive entry.')
            names.add(name.casefold())
        if contents.testzip() is not None or json.loads(contents.read('manifest.json')) != expected:
            raise ValueError('Archive manifest differs from the tested source manifest.')
        if PACKAGES[package]['type'] == 'system':
            contents.getinfo(expected['entry'])
        if package == 'dnd5e':
            paths = expected.get('content', {}).get('compendiums', [])
            if not paths:
                raise ValueError('The SRD system must declare its compiled compendiums.')
            for path in paths:
                collection = json.loads(contents.read(path))
                if not isinstance(collection.get('packs'), list) or not collection['packs']:
                    raise ValueError('Invalid compiled compendium collection.')
        if package in {'swade', 'swade-server'}:
            if 'content' in expected or any(name.lower().endswith('.pdf') for name in names):
                raise ValueError('Savage Worlds compatibility packages cannot ship game content or PDFs.')
            if SAVAGE_NOTICE not in contents.read('NOTICE.md').decode('utf-8'):
                raise ValueError('The exact Savage Worlds permission notice is required.')
            if package == 'swade':
                contents.getinfo('assets/branding/savage-worlds-logo.png')
    published = source_release_archive(package, expected['version'], filename, source_sha)
    if archive_payload(published) != archive_payload(archive.read_bytes()):
        raise ValueError('Published source release payload differs from the tested build.')
    # Preserve already published bytes: DEFLATE output can vary between zlib
    # and zlib-ng even when every uncompressed file and permission is identical.
    (directory / filename).write_bytes(published)
    return describe(package, directory, source_sha)


def describe(package, directory, source_sha):
    if not re.fullmatch('[0-9a-f]{40}', source_sha):
        raise ValueError('A full source commit SHA is required.')
    archives = list(directory.glob('*.zip'))
    if len(archives) != 1 or archives[0].stat().st_size > 100 * 1024 * 1024:
        raise ValueError('Expected one release ZIP up to 100 MB.')
    archive = archives[0]
    with zipfile.ZipFile(archive) as contents:
        matches = [item for item in contents.infolist() if item.filename == 'manifest.json']
        if len(matches) != 1 or matches[0].file_size > 65536:
            raise ValueError('Expected one small root manifest.')
        manifest = json.loads(contents.read(matches[0]))
    package = PACKAGES[package]
    validate_manifest(package, manifest)
    if archive.name != Path(archive.name).name or not re.fullmatch(r'[A-Za-z0-9_.-]+\.zip', archive.name):
        raise ValueError('Invalid archive name.')
    tag = package['id'] + '-v' + manifest['version']
    return archive, {
        'id': package['id'], 'name': package.get('catalog_name', manifest['name']), 'version': manifest['version'],
        'description': package.get('catalog_description', manifest.get('description', manifest['name'])),
        'sdk': manifest['sdk']['requires'], 'type': package.get('type', 'module'), 'tags': package['tags'],
        'download': f'https://github.com/Gravewright/marketplace/releases/download/{tag}/{archive.name}',
        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    }, tag


def sign_record(record, pem, key_id, keys):
    key = load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError('Expected an Ed25519 signing key.')
    public = base64.b64encode(key.public_key().public_bytes_raw()).decode()
    if keys.get(key_id) != public:
        raise ValueError('Signing key does not match the trusted public key.')
    record = {**record, 'keyId': key_id}
    raw = json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    return {**record, 'signature': base64.b64encode(key.sign(raw)).decode()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'inspect', 'sign', 'publish'])
    parser.add_argument('--package', choices=PACKAGES, required=True)
    parser.add_argument('--directory', type=Path, default=Path('release'))
    parser.add_argument('--source', type=Path, default=Path('source'))
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.package, args.source, args.directory, args.source_sha)
        return
    archive, record, tag = describe(args.package, args.directory, args.source_sha)
    catalog_path = ROOT / 'gravewright.marketplace.json'
    catalog = read(catalog_path)
    if any((item['id'], item['version']) == (record['id'], record['version']) for item in catalog):
        raise ValueError('This module version is already published. Bump its version first.')
    if args.command == 'inspect':
        summary = f"Package: {record['id']} {record['version']}\nSource: {PACKAGES[args.package]['repo']}@{args.source_sha}\nSHA-256: {record['sha256']}\n"
        print(summary)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
                stream.write('### Release awaiting approval\n\n```text\n' + summary + '```\n')
        return
    if args.command == 'sign':
        signed = sign_record(record, os.environ['SIGNING_PRIVATE_KEY'].encode(),
                             os.environ['SIGNING_KEY_ID'], read(ROOT / 'trusted-keys.json'))
        write(args.directory / 'catalog.json', [signed])
        (args.directory / 'SHA256SUMS.txt').write_text(f"{record['sha256']}  {archive.name}\n", encoding='utf-8')
        write(args.directory / 'provenance.json', {'repository': PACKAGES[args.package]['repo'],
                                                  'commit': args.source_sha, 'sha256': record['sha256']})
        return
    signed = read(args.directory / 'catalog.json')[0]
    if {k: v for k, v in signed.items() if k not in {'keyId', 'signature'}} != record:
        raise ValueError('Signed record does not match the approved archive.')
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(read(ROOT / 'trusted-keys.json')[signed['keyId']]))
    canonical = json.dumps({k: v for k, v in signed.items() if k != 'signature'}, sort_keys=True,
                           separators=(',', ':'), ensure_ascii=True).encode('ascii')
    public.verify(base64.b64decode(signed['signature']), canonical)
    # Create a draft first. No existing tag/release or signed record is overwritten.
    subprocess.run(['gh', 'release', 'create', tag, str(archive), str(args.directory / 'catalog.json'),
                    str(args.directory / 'SHA256SUMS.txt'), str(args.directory / 'provenance.json'),
                    '--repo', 'Gravewright/marketplace', '--target', os.environ['GITHUB_SHA'],
                    '--draft', '--title', record['name'] + ' ' + record['version'],
                    '--notes', f"Source: {PACKAGES[args.package]['repo']}@{args.source_sha}\nSHA-256: {record['sha256']}"], check=True)
    subprocess.run(['gh', 'release', 'edit', tag, '--repo', 'Gravewright/marketplace',
                    '--tag', tag, '--target', os.environ['GITHUB_SHA'], '--draft=false'], check=True)
    # Confirm the published download before offering a signed catalog entry.
    # This step has no private key and executes no source-package code.
    with tempfile.TemporaryDirectory(prefix='marketplace-download-') as temporary:
        subprocess.run(['gh', 'release', 'download', tag, '--repo', 'Gravewright/marketplace',
                        '--pattern', archive.name, '--dir', temporary], check=True)
        if hashlib.sha256((Path(temporary) / archive.name).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Published release download differs from the approved archive.')
    write(catalog_path, [*catalog, signed])
    subprocess.run(['python', str(ROOT / 'scripts/validate_catalog.py')], check=True)
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git', 'add', 'gravewright.marketplace.json'], check=True)
    subprocess.run(['git', 'commit', '-m', f"Publish {record['id']} {record['version']}"], check=True)
    subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)


if __name__ == '__main__':
    main()
