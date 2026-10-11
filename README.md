# Gravewright Marketplace

Package signing and publishing now run in this repository's **Sign and publish
package** GitHub Actions workflow, behind the `release-signing` environment's
required approval. New release assets are hosted here; existing package URLs stay
unchanged. See [publication, maintainers and key recovery](PUBLISHING.pt-BR.md).

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
| [Translator](https://github.com/Gravewright/translator) | [v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright.translator-v0.1.1) | Owner: Installed modules → Activate languages. Users: internal Settings → Interface language. |
| [Gravewright 3D Dice](https://github.com/Gravewright/Gravewright-3D-Dice) | [v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright-3d-dice-v0.1.1) | Activate per table in Extensions; appearance preferences are personal. |

Translator offers English, Brazilian Portuguese and Spanish. It requires a host with `manifest.locales` support and global language activation. Version 0.1.1 includes current document permissions, sharing, references, window and package-management translations. See the package README for coverage limits and validation instructions.

Use **Update** in installed module lists to install a newer signed release while preserving activation and saved settings. **Remove** lists affected tables for confirmation, then removes the package from those tables. Previously published package archives and signatures remain unchanged.

## Catalog format

The root is a **JSON list of signed records**, not the obsolete `schema_version/packages/revoked` object. Each record includes `id`, `version`, `sdk`, `download` (HTTPS ZIP), `sha256`, `keyId` and `signature`. Optional signed display metadata includes `name` and `description`. Revocation is a signed record with `status: "revoked"`.

Sign the UTF-8/ASCII JSON bytes of the record without `signature`, with sorted keys, compact separators and ASCII escapes (`json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')`). Store the Ed25519 signature as base64. Changing any signed field requires a new signature. Published ID/version artifacts are immutable; publish a new version for changed bytes.

ZIP roots contain `manifest.json` and its declared entry. Ordinary modules activate per campaign. Manifests with `system` register installed systems; manifests with `locales` provide declarative installation-wide language catalogs. Marketplace ZIPs cannot install Python apps into the host process.

Validate before committing, using an environment with `cryptography`:

```sh
python scripts/validate_catalog.py
```

[Português](README.pt-BR.md)

## Creator-defined categories

Add `"type": "module"` (or `"system"`) and a free-text `tags` list to a signed record, for example:

```json
"tags": ["Tradução", "Idiomas", "Interface"]
```

The VTT builds the installation modal's categories from these tags, separately for systems and modules. Tags are displayed as supplied by the creator. Up to 24 unique, nonempty tags of 64 characters are accepted, including Unicode. Tags must be included before signing: changing them invalidates the previous signature. Catalog metadata can be re-signed without replacing an unchanged release ZIP or its SHA-256. Older hosts without tag support require the current host integration.
