# Blender Pro VPS Design

## Purpose
Build an isolated, reproducible Blender production stack for headless scene automation and CPU/GPU-ready rendering without modifying existing Traefik, 9router, Obsidian, or Docker service topology.

## Core architecture
- `/root/blender-pro-control`: Git-tracked source, tests, deployment scripts, systemd units, schemas, and documentation.
- `/opt/blender-pro`: immutable runtime, exact Blender releases, pinned packages, wrappers, profiles, locks, and installed skills.
- `/srv/blender-pro`: durable projects, published assets, previews, final renders, and job metadata.
- `/var/cache/blender-pro`: regenerable Blender/job/render caches.
- `/var/log/blender-pro`: structured operational logs.
- `/run/blender-pro`: transient runtime state only.

## Trust boundaries
- `blender-admin`: deployment/promotion operations only.
- `blender-agent`: structured automation gateway; no unrestricted Python/shell API.
- `blender-render`: deterministic preflight/preview/final render worker; cannot modify runtime.
- Render-safe profile defaults to no network and no automatic untrusted script execution.
- Asset-fetch profile is separate and is the only profile allowed to use BlenderKit/network access.

## Runtime policy
- Pin Blender 5.2.0 LTS initially and record official archive SHA256 plus build hash.
- Install future patch releases side-by-side and switch `/opt/blender-pro/current` atomically only after qualification.
- Keep Blender Python isolated from system Python.
- Record Node Wrangler, Rigify, BlenderKit, and any future extensions in explicit lock metadata.

## Production flow
manifest -> path/policy validation -> Blender scene preflight -> low-cost same-engine preview -> final render -> postcheck -> atomic output promotion.

## Asset flow
incoming -> inspect/localize/normalize -> work -> immutable versioned publish -> linked library consumption.

## Agent policy
Expose structured actions only: scene inspection, verification, preview, render submission/status, and approved asset operations. Do not expose arbitrary Python, arbitrary shell, unrestricted filesystem reads/writes, or public MCP ports.

## Acceptance
The deployment is accepted only when exact Blender version/hash, headless startup, smoke preflight, preview, final render, path-security tests, worker isolation, and protected-service before/after checks all pass.
