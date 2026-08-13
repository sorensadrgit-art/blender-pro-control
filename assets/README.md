# Blender Pro Asset Library

Production assets use four stages under `/srv/blender-pro/assets`:

- `incoming/` — untrusted downloaded/imported content.
- `work/` — editable normalization and build area.
- `published/` — immutable versioned production libraries.
- `linked/` — optional curated aliases/catalog integration.
- `catalog/` — catalog metadata.

## Publishing contract

Publish only existing `.blend` files from `work/` using `blender-asset-publish`.
Versions use `vNNN` or higher and are immutable: an existing version is never overwritten.
Each published version contains `<asset-name>.blend` plus `asset.json` with its SHA-256.

## Linking contract

Production scenes link from explicit published versions, for example:
`/srv/blender-pro/assets/published/props/hero-cube/v001/hero-cube.blend`.
A published library should expose one clearly named root collection such as `ASSET_HeroCube`.
Use Library Overrides only when a scene needs controlled local edits or animation.
