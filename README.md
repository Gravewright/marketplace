# Gravewright Marketplace

[Português (Brasil)](README.pt-BR.md)

The official catalog of modules and recipes for [Gravewright](https://github.com/Gravewright).

Gravewright reads [`gravewright.marketplace.json`](./gravewright.marketplace.json) from this repository to discover available modules and recipes.

## Submit a project

To publish a module or recipe in the marketplace:

1. Publish your project in a public repository.
2. Create a versioned release.
3. Provide an HTTPS manifest pointing to the release ZIP.
4. Calculate and publish the ZIP SHA-256 digest.
5. [Open an issue](https://github.com/Gravewright/marketplace/issues/new) requesting inclusion.

Include the following information:

- Project name
- Short description
- Type: module or recipe
- Module kind, when applicable
- Repository URL
- Manifest or recipe URL
- Current version
- License
- Maintainer name

Inclusion is not automatic. The project will be reviewed before it is added to the catalog.

## Module requirements

The manifest must be available over HTTPS and point to an immutable release ZIP:

```json
{
  "name": "fog-of-war",
  "kind": "addon",
  "provider": "community",
  "version": "1.2.0",
  "entry": "./index.js",
  "exports": {
    "get": []
  },
  "download_url": "https://github.com/example/fog-of-war/releases/download/v1.2.0/fog-of-war.zip",
  "download_sha256": "zip-file-sha256"
}
```

The URL registered in the marketplace must point to a stable manifest, such as:

```text
https://example.org/fog-of-war/latest.json
```

This manifest may be updated when a new release is published. Its referenced ZIP must remain versioned and immutable. The marketplace does not install code directly from the `main` branch.

## Recipe requirements

Recipes group modules into a complete Gravewright project:

```json
{
  "schema_version": 1,
  "kind": "recipe",
  "name": "dark-fantasy-table",
  "title": "Dark Fantasy Table",
  "version": "1.0.0",
  "description": "A server and modules for a dark fantasy table.",
  "modules": [
    {
      "manifest_url": "https://example.org/server/latest.json",
      "version": "^1.0.0",
      "state": "active"
    },
    {
      "manifest_url": "https://example.org/fog-of-war/latest.json",
      "version": "~1.2.0",
      "state": "active"
    }
  ]
}
```

A recipe:

- Is not an executable module.
- Cannot contain scripts.
- Must produce a project with exactly one active `server` module.
- May use exact versions, `*`, `^`, or `~` constraints.

## Security

Before installation, Gravewright:

- Accepts only public HTTPS URLs.
- Blocks private and reserved hosts.
- Validates redirects.
- Limits download sizes.
- Verifies the ZIP SHA-256 digest.
- Rejects path traversal and symbolic links.
- Validates the manifest included in the package.
- Does not overwrite installed modules.
- Prepares every module in a recipe before committing the installation.

An entry may be removed or added to the revoked releases list if it presents a risk to users.

## Catalog

[`gravewright.marketplace.json`](./gravewright.marketplace.json) follows this structure:

```json
{
  "schema_version": 1,
  "packages": [],
  "revoked": []
}
```

Catalog changes are made by maintainers after reviewing requests submitted through issues.

## Removal and revocation

To request project removal or report a vulnerability:

- Open an issue for public, non-sensitive matters.
- Do not disclose exploitable vulnerability details in public issues.
- Use the organization's private security reporting channel for security issues.

## License

Listed projects remain subject to their own licenses.

Being listed in the Gravewright Marketplace does not transfer ownership, responsibility, or rights over third-party modules and recipes.
