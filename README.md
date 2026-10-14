# Gravewright Marketplace

Package signing and publishing now run in this repository's **Sign and publish
package** GitHub Actions workflow, behind the `release-signing` environment's
required approval. New release assets are hosted here; existing package URLs stay
unchanged. See [publication, maintainers and key recovery](PUBLISHING.pt-BR.md).
English instructions: [Publishing](PUBLISHING.md).

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
| [Translator](https://github.com/Gravewright/translator) | [v0.1.2](https://github.com/Gravewright/marketplace/releases/tag/gravewright.translator-v0.1.2) | Owner: Installed modules → Activate languages. Users: internal Settings → Interface language. |
| [Gravewright 3D Dice](https://github.com/Gravewright/Gravewright-3D-Dice) | [v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright-3d-dice-v0.1.1) | Activate per table in Extensions; appearance preferences are personal. |
| [DnD 5e SRD](https://github.com/Gravewright/dnd-srd-5e) | [v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright.5e-srd-v0.1.1) | One package under Systems, including compendiums and automation. Works on VTT 0.2.3. |
| [Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright) | [v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright.savage-worlds-v0.1.1) | One package under Systems, including its automation. Works on VTT 0.2.3. |

Translator offers English, Brazilian Portuguese and Spanish. It requires a host with `manifest.locales` support and global language activation. Version 0.1.2 includes reviewed interface catalogs and module integration documentation. See the package README for coverage limits and validation instructions.

## DnD 5e SRD

[DnD 5e SRD](https://github.com/Gravewright/dnd-srd-5e) **0.1.1** includes the
2014 (SRD 5.1) and 2024 (SRD 5.2.1) profiles in one system package for the
published **Gravewright VTT 0.2.3**. Install it under **Systems** and select the
version for your table. Sheets, item templates, licensed SRD compendiums,
initiative and effect automation belong to this package. The GM advances combat
through the system tracker. The VTT core and its release remain unchanged.

The only current package ID is `gravewright.5e-srd` (`type: "system"`). No server
extension or Python activation is required. Earlier installations can review
the old companion in the system's Customize window; the host owner authorizes
deactivation and removal after reviewing affected tables. Existing actors,
items, table settings and historical release signatures are preserved.

English is the default interface language. Activate the official Translator
0.1.2 for Portuguese or Spanish; authored SRD compendium text remains in English.
The catalog describes the application requirement but does not enforce a minimum
VTT version. See the source repository for licensing and supported automation.

## Savage Worlds Compatibility Package for Gravewright

[Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright)
0.1.1 provides editable SWADE sheets, blank item structures, native action-card
initiative and package-owned automation. It includes no game content or compendiums.
It works on the published **Gravewright VTT 0.2.3**, using its existing public
APIs. This system update does not require a new VTT release.

The single package uses `gravewright.savage-worlds` (`type: "system"`). Install
it under **Systems** and select it for the table. Sheets, assets and every Savage
Worlds rule stay inside this JavaScript system. The GM uses its tracker to advance
turns and effect clocks. Persisted operations resume interrupted updates without
applying completed steps twice. New installations need only this system ZIP.
If an old server-only extension is still active, use the system's migration
controls to deactivate and remove it before enabling package-owned turn clocks.
The migration preserves characters, items and table settings.

English is the default interface language. Activate the official Translator
0.1.2 for Brazilian Portuguese or Spanish and choose a personal language in account
settings. In the table's **Extensions → Personalize**, choose one of three original
action-card decks and create it in the native deck manager, or select an existing
deck. Cards come from the configured deck. Publication uses the signed single-package
[release workflow](PUBLISHING.md#savage-worlds-compatibility-package-for-gravewright);
the source repository documents installation, permissions and supported automation.

Use **Update** in installed module lists to install a newer signed release while preserving activation and saved settings. **Remove** lists affected tables for confirmation, then removes the package from those tables. Previously published package archives and signatures remain unchanged.

## Catalog format

The root is a **JSON list of signed records**, not the obsolete `schema_version/packages/revoked` object. Each record includes `id`, `version`, `sdk`, `download` (HTTPS ZIP), `sha256`, `keyId` and `signature`. Optional signed display metadata includes `name` and `description`. Revocation is a signed record with `status: "revoked"`.

Sign the UTF-8/ASCII JSON bytes of the record without `signature`, with sorted keys, compact separators and ASCII escapes (`json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')`). Store the Ed25519 signature as base64. Changing any signed field requires a new signature. Published ID/version artifacts are immutable; publish a new version for changed bytes.

ZIP roots contain `manifest.json` and its declared entry, when present. Ordinary modules activate per campaign. Manifests with `system` register installed systems; manifests with `locales` provide declarative installation-wide language catalogs. A `type: "django"` record can install a trusted server extension; only the host owner can activate it through the managed Runner. Downloading a package never imports its Python code automatically.

Validate before committing, using an environment with `cryptography`:

```sh
python scripts/validate_catalog.py
```

[Português](README.pt-BR.md)

## Creator-defined categories

Add `"type": "module"`, `"system"` or `"django"` and a free-text `tags` list to a signed record, for example:

```json
"tags": ["Tradução", "Idiomas", "Interface"]
```

The VTT builds the installation modal's categories from these tags, separately for systems and modules. Tags are displayed as supplied by the creator. Up to 24 unique, nonempty tags of 64 characters are accepted, including Unicode. Tags must be included before signing: changing them invalidates the previous signature. Catalog metadata can be re-signed without replacing an unchanged release ZIP or its SHA-256. Older hosts without tag support require the current host integration.
