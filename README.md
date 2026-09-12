# Gravewright Marketplace

Signed module and system catalog consumed by Gravewright VTT. Packages are real GitHub release assets; installed packages are listed from the host database.

## Host configuration

```dotenv
GRAVEWRIGHT_MARKETPLACE_URL=https://raw.githubusercontent.com/Gravewright/marketplace/main/gravewright.marketplace.json
GRAVEWRIGHT_MARKETPLACE_KEYS_FILE=/absolute/path/to/marketplace/trusted-keys.json
```

`trusted-keys.json` contains public Ed25519 verification keys. Review and install this file locally; private signing keys must never be committed. Restart the VTT after changing its environment.

## Available packages

| Package | Release | Activation |
| --- | --- | --- |
| [Translator](https://github.com/Gravewright/translator) | [v0.1.0 preview](https://github.com/Gravewright/translator/releases/tag/v0.1.0) | Owner: Installed modules → Activate languages. Users: internal Settings → Interface language. |

Translator offers English, Brazilian Portuguese and Spanish. It requires a host with `manifest.locales` support and global language activation; older Gravewright hosts do not support this preview. It is not a per-table extension. See the package README for coverage limits and validation instructions.

## Catalog format

The root is a **JSON list of signed records**, not the obsolete `schema_version/packages/revoked` object. Each record includes `id`, `version`, `sdk`, `download` (HTTPS ZIP), `sha256`, `keyId` and `signature`. Optional signed display metadata includes `name` and `description`. Revocation is a signed record with `status: "revoked"`.

Sign the UTF-8/ASCII JSON bytes of the record without `signature`, with sorted keys, compact separators and ASCII escapes (`json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')`). Store the Ed25519 signature as base64. Changing any signed field requires a new signature. Published ID/version artifacts are immutable; publish a new version for changed bytes.

ZIP roots contain `manifest.json` and its declared entry. Ordinary modules activate per campaign. Manifests with `system` register installed systems; manifests with `locales` provide declarative installation-wide language catalogs. Marketplace ZIPs cannot install Python apps into the host process.

Validate before committing, using an environment with `cryptography`:

```sh
python scripts/validate_catalog.py
```

[Português](README.pt-BR.md)
