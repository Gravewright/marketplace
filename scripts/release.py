"""Sign approved archives and publish them from the central Marketplace repo."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    'dice3d': {'id': 'gravewright-3d-dice', 'repo': 'Gravewright/Gravewright-3D-Dice',
               'tags': ['Dados', '3D', 'Rolagens']},
    'translator': {'id': 'gravewright.translator', 'repo': 'Gravewright/translator',
                   'tags': ['Tradução', 'Idiomas', 'Interface']},
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


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
    if manifest['id'] != package['id'] or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', manifest['version']):
        raise ValueError('Unexpected module ID or invalid stable version.')
    if archive.name != Path(archive.name).name or not re.fullmatch(r'[A-Za-z0-9_.-]+\.zip', archive.name):
        raise ValueError('Invalid archive name.')
    tag = package['id'] + '-v' + manifest['version']
    return archive, {
        'id': package['id'], 'name': manifest['name'], 'version': manifest['version'],
        'description': manifest.get('description', manifest['name']),
        'sdk': manifest['sdk']['requires'], 'type': 'module', 'tags': package['tags'],
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
    parser.add_argument('command', choices=['inspect', 'sign', 'publish'])
    parser.add_argument('--package', choices=PACKAGES, required=True)
    parser.add_argument('--directory', type=Path, default=Path('release'))
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
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
    subprocess.run(['gh', 'release', 'edit', tag, '--repo', 'Gravewright/marketplace', '--draft=false'], check=True)
    write(catalog_path, [*catalog, signed])
    subprocess.run(['python', str(ROOT / 'scripts/validate_catalog.py')], check=True)
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git', 'add', 'gravewright.marketplace.json'], check=True)
    subprocess.run(['git', 'commit', '-m', f"Publish {record['id']} {record['version']}"], check=True)
    subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)


if __name__ == '__main__':
    main()
