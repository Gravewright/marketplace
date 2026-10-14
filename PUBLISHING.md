# Publishing signed packages

The **Sign and publish package** workflow builds public source repositories
without access to the private signing key. Its `publish` job requires approval
through the `release-signing` environment, restricted to the Marketplace `main`
branch. The temporary `GITHUB_TOKEN` writes only to this repository.

1. Commit and push the source version. Never reuse a published package ID/version.
2. Dispatch the workflow from `main`, selecting `dice3d`, `translator`, `dnd5e`,
   `dnd5e-server` or `swade` and the source commit SHA, tag or branch.
3. Review the resolved full source SHA, build tests, artifact and archive SHA-256.
4. Approve the pending deployment as an authorized environment reviewer.
5. The workflow signs the approved ZIP, creates a release draft with the archive,
   checksum, signed `catalog.json` and `provenance.json`, then publishes it. It
   downloads the public archive and verifies its digest before updating the catalog.

If catalog validation or pushing fails after release publication, the signed
record remains downloadable from that release. Review and append the unchanged
record to `gravewright.marketplace.json`, run `python scripts/validate_catalog.py`
and commit it. Do not replace a published archive or reuse its version.

## DnD 5e SRD

Source repository: [Gravewright/dnd-srd-5e](https://github.com/Gravewright/dnd-srd-5e).
Keep the stable IDs `gravewright.5e-srd` and `gravewright.5e-srd-server`; display
names are **DnD 5e SRD** and **DnD 5e SRD - Server Rules**. Both manifests must
declare the same version.

Publish the source repository's public `v{version}` release and its versioned ZIP
assets first. Dispatch `dnd5e-server`, then `dnd5e`, using the **same full source
commit SHA**. Each dispatch tests the source and builds both artifacts. It checks
that the source Git tag resolves to that exact commit, then downloads the selected
public release ZIP with its GitHub SHA-256 and size checks. Every ZIP path,
permission and uncompressed file must match the tested build; extra entries,
duplicates and changed payloads are rejected. The original published ZIP bytes
become the sole artifact for approval and signing. This preserves one immutable
ID/version archive even when zlib and zlib-ng produce different DEFLATE streams.
The workflow serializes releases to prevent concurrent
catalog pushes. Publishing the companion first makes its required download
available before offering the browser system.

The build tests the system against a pinned VTT 0.2.1 checkout via
`GRAVEWRIGHT_TEST_HOST_ROOT`. Host dependencies come from its locked environment
and are not bundled in the system packages. JavaScript rules, translations,
compiled compendiums and trusted server rules are checked. Rebuilding compendiums
from the licensed, pinned SRD PDF/YAML sources is a separate source-project task.
After building, `scripts/validate_package.py` checks generated data, translations,
compendiums, provenance, exact ZIP contents, CRCs, SHA-256 and licensing notices.

`scripts/release.py prepare` checks paired identities, versions, names and package
types, requires the public source release, selects its expected versioned archive,
checks safe ZIP paths and compares its entire payload with the tested build.
The archive manifest must match the tested source. The browser record is
`type: "system"`; the server companion is `type: "django"`, requiring explicit
host-owner activation and a managed Runner restart. The signing job never checks
out or executes source-package code.

Document the **VTT 0.2.1 minimum**, companion of the same version and optional
Translator 0.1.2 for additional interface languages. Catalog records do not
support `dependencies` or a minimum host version field; adding unknown fields
makes the VTT reject the record. SDK `>=1.0.0 <2.0.0` alone cannot express the
minimum application version. Verify both public ZIPs and signed records, then
test installation in VTT 0.2.1 before updating availability links.

## Savage Worlds Compatibility Package for Gravewright

Source repository: [Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright).
Publish only `gravewright.savage-worlds` (`system`). Its one manifest contains
browser entry, system metadata and `django` server automation. Publish the source
`v{version}` release with its single system ZIP and checksum first, then dispatch
**`swade`** with the full source SHA. The workflow verifies the immutable public
source archive, its SHA-256 and every tested payload byte before approval and
signing. Package code never runs with the signing key available.

The ZIP is `gravewright-savage-worlds-{version}.zip`, including browser assets,
translations and `gravewright_swade/` server code. Preserve the exact Pinnacle
permission notice and approved logo. Include no compendiums, game content or book
PDFs. Publication retires the old server-only catalog entry atomically when the
verified replacement record is appended. Historical assets and signatures remain
unchanged; the workflow no longer offers a separate server-package build.

This release requires **VTT 0.2.4 or later**, including generic support for combined
system packages, `context.host` and `card.asset.upload`. The workflow tests against
the public `v0.2.4` host tag. The catalog
cannot enforce a minimum application version; older hosts must update their core.
Check the public archive hashes before dispatching. Install and activate the official
Translator 0.1.2 for Portuguese or Spanish; English is the default. Installing
the system is followed by host-owner activation of its automation in **Systems**
and a managed Runner restart.

## Signing keys and recovery

`SIGNING_PRIVATE_KEY` is an environment secret; `SIGNING_KEY_ID` is its environment
variable. The signer verifies the derived public key against `trusted-keys.json`
before signing. Private keys are never written to releases, logs or Git.

Keep approved maintainers in the protected environment and an access-controlled
backup of the private key in a password manager, plus a separate recovery copy.
GitHub secrets cannot be downloaded after creation. A lost workstation does not
delete secrets held by GitHub. The existing setup allows an authorized reviewer
to approve a workflow they started; enable **Prevent self-review** when another
qualified reviewer is available.

For rotation, add the new public key without removing old keys, distribute the
updated trusted registry and pinned installer digest to hosts, then replace the
environment secret and key ID. Verify a signature before publishing. The lost
`gravewright-2026` private key is no longer used, but its public key must remain
to verify historical releases. Handle compromised-key revocation separately.

[Português](PUBLISHING.pt-BR.md)
