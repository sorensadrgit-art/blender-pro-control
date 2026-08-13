# BlenderKit Production Policy

BlenderKit is a staging capability, never a production render dependency.

- Approved release: `3.21.0.260628` (`3.21.0-260628` manifest version).
- Package SHA-256: `fbeee0f603b5ca23aeb493d7826051d0d47ec2dd28ce1469b1a0f3197d2e1e8c`.
- Install scope: `asset-fetch` only.
- Install root: `/var/lib/blender-pro/extensions/asset-fetch/user_default/blenderkit`.
- Declared permissions: filesystem and network.
- `render-safe` must not contain or enable BlenderKit and always runs with Blender offline mode.

## Asset flow

1. Search/download only in the `asset-fetch` profile.
2. Place imported content in `incoming/` or `work/`.
3. Localize external textures/dependencies and validate paths/licensing metadata.
4. Publish an immutable internal `.blend` version under `assets/published/`.
5. Production scenes link only to the internal published path, never the BlenderKit cache.

Updates are explicit: verify the new upstream artifact, record version/commit/hash in `extensions.lock.json`, qualify it, then promote it. Automatic extension updates are not part of production rendering.
