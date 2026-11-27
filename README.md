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
| [DnD 5e SRD](https://github.com/Gravewright/dnd-srd-5e) | [v0.2.2](https://github.com/Gravewright/marketplace/releases/tag/gravewright.5e-srd-v0.2.2) | One package under Systems, including compendiums and automation. Works on VTT 0.2.3; native initiative batches and compendium folders on VTT 0.3.8. |
| [Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright) | [v0.1.4](https://github.com/Gravewright/marketplace/releases/tag/gravewright.savage-worlds-v0.1.4) | One package under Systems, including its automation. Works on VTT 0.2.3. |

Translator offers English, Brazilian Portuguese and Spanish. It requires a host with `manifest.locales` support and global language activation. Version 0.1.2 includes reviewed interface catalogs and module integration documentation. See the package README for coverage limits and validation instructions.

## DnD 5e SRD

[DnD 5e SRD 0.2.2](https://github.com/Gravewright/marketplace/releases/tag/gravewright.5e-srd-v0.2.2)
includes the **2014 / SRD 5.1** and **2024 / SRD 5.2.1** profiles in one
signed browser system. As host owner, refresh the Marketplace, open **Systems**
and install or update **DnD 5e SRD**. In each existing table, select **0.2.2** in
**Settings → Extensions**, then reload open table pages. Keep the previous
version installed if you need to select it again for rollback.

The package supports the released **Gravewright VTT 0.2.3** and SDK 1.x.
On **VTT 0.3.8**, it uses native initiative batches and groups its twenty-two
compendium packs into **DnD 5e SRD**, with one subfolder per edition. Older hosts
keep sequential initiative recovery and the flat compendium list.

Version 0.2.2 corrects supported automations checked against the official SRD,
including Dexterity-based AC, Constitution-based HP, protection items and the
Defense fighting style. Its licensed collections contain **2,535 item entries**,
**317 SRD 5.1 monsters** and **330 SRD 5.2.1 monsters**. Players can copy readable
compendium items into editable sheets; server read permissions still apply.
Library imports and Effects remain GM-only. The collections are partial, and
rules without supported declarative automation remain manual.

The stable package ID is `gravewright.5e-srd` (`type: "system"`). Sheets, item
templates, translations, settings, initiative and supported turn automation
belong to this single package. The GM advances combat through its tracker.
New installations require no server extension or Python activation. Earlier
installations can review an old companion in the system's Customize window;
the host owner authorizes deactivation and removal after reviewing affected
tables. Existing actors, items and table settings are preserved.

English is the default interface language. Activate the official Translator
**0.1.2 or newer** for Portuguese or Spanish; authored SRD compendium text
remains in English. The catalog describes the application requirement but does
not enforce a minimum VTT version. The
[source release](https://github.com/Gravewright/dnd-srd-5e/releases/tag/v0.2.2)
provides the same ZIP for local installation. See the source repository for
licensing, supported automation and installation guidance.

## Savage Worlds Compatibility Package for Gravewright

Version **0.1.4** further compacts sheets and names actor types **Wild Card** and **Extra**. The GM chooses the type at creation; the sheet setup no longer offers a type selector. Existing actor identifiers and saved data are preserved.

[Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright)
0.1.4 provides editable SWADE sheets, blank item structures, native action-card
initiative and package-owned automation. It includes no game content or compendiums.
It works on the published **Gravewright VTT 0.2.3**, using its existing public
APIs. This system update does not require a new VTT release.

Version 0.1.2 compacts actor sheets, roll windows and all thirteen item editors,
with interface text of at least 12 px. Skills and other named lists appear in
alphabetical order in the selected interface language without rearranging saved
collections. Each skill offers a linked attribute selector while retaining its
own die and modifier. Native item-directory and compendium-browser layout updates
belong to the VTT, separately from this system ZIP.

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
