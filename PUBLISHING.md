# Publishing signed packages

The **Sign and publish package** workflow builds public source repositories
without access to the private signing key. Its `publish` job requires approval
through the `release-signing` environment, restricted to the Marketplace `main`
branch. The temporary `GITHUB_TOKEN` writes only to this repository.

1. Commit and push the source version. Never reuse a published package ID/version.
2. Dispatch the workflow from `main`, selecting `dice3d`, `translator`, `dnd5e`,
   or `swade` and the source commit SHA, tag or branch.
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

The source is `Gravewright/dnd-srd-5e`. Preserve the system ID
`gravewright.5e-srd` and display name **DnD 5e SRD**. Each release contains one
browser system ZIP with its sheets, item templates, licensed SRD compendiums,
translations and JavaScript automation. Do not publish another server package.

Publish `v{version}` in the source repository with
`gravewright-5e-srd-{version}.zip` and its checksum. Dispatch **`dnd5e`** once
with the full source commit SHA. The workflow checks out the unchanged public
VTT 0.2.3 commit for its SDK and native installer tests. It runs JavaScript,
translation and compendium checks, builds the ZIP before the installation
tests, and validates exact runtime files, CRC, SHA-256 and license notices.
Existing compiled SRD data and provenance remain intact; rebuilding licensed
source material is a separate operation.

`scripts/release.py prepare` verifies the source tag and public release,
download metadata and every payload byte and mode against the tested build.
The immutable public source ZIP becomes the single artifact approved and signed.
Systems with Django manifests or Python runtime files are rejected. The signer
does not execute source-package code and receives only the approved ZIP.

After publishing and verifying the replacement download, the same catalog commit
adds the new `type: "system"` record and retires all `gravewright.5e-srd-server`
entries. Preserve every other historical record, archive URL and signature.
Do not retire the old entry before the new signed system is available.
Verify all catalog signatures and install the public ZIP in an isolated original
VTT 0.2.3 before updating availability links. Never publish a VTT release for
this system-package update.

The catalog supports only its documented fields. Put the VTT 0.2.3 requirement
and optional official Translator in the description and documentation; do not
invent dependency or minimum-host fields. The SDK remains `>=1.0.0 <2.0.0`.
Existing installations use the system's owner-authorized migration controls to
deactivate the old companion through the native restart flow; removing it is
a separate confirmation after reviewing affected tables. New installations
need only the system ZIP. The GM advances browser-owned combat automation from
the table; no Python extension is activated.

## Savage Worlds Compatibility Package for Gravewright

Source repository: [Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright).
Publish only `gravewright.savage-worlds` (`system`). Its one manifest contains
browser entry, system metadata and JavaScript automation. Publish the source
`v{version}` release with its single system ZIP and checksum first, then dispatch
**`swade`** with the full source SHA. The workflow verifies the immutable public
source archive, its SHA-256 and every tested payload byte before approval and
signing. Package code never runs with the signing key available.

The ZIP is `gravewright-savage-worlds-{version}.zip`, including browser assets,
translations and all package-owned automation. Include no Python runtime files.
Preserve the exact Pinnacle
permission notice and approved logo. Include no compendiums, game content or book
PDFs. Publication retires the old server-only catalog entry atomically when the
verified replacement record is appended. Historical assets and signatures remain
unchanged; the workflow no longer offers a separate server-package build.

This release targets the original published **VTT 0.2.3** and its existing public
APIs, including `context.host` and `card.asset.upload`. The workflow tests against
the public `v0.2.3` host tag without modifying its source. The catalog
cannot enforce a minimum application version; older hosts must update their core.
Check the public archive hashes before dispatching. Install and activate the official
Translator 0.1.2 for Portuguese or Spanish; English is the default. Installing
the system and selecting it for the table enables its package-owned interface.
Turn advancement and clock updates use the GM's tracker and persisted retry
journals. Existing server-only installations use the system's migration controls
to remove the legacy extension; fresh installations need no server extension.

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
