# Blender Pro VPS Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, isolated Blender 5.2 LTS headless production foundation on the VPS without modifying Traefik, 9router, Obsidian, or existing Docker networks.

**Architecture:** Keep source/control code in `/root/blender-pro-control` and deploy a root-owned runtime to `/opt/blender-pro`. Durable projects/assets/renders live in `/srv/blender-pro`; caches and logs live under `/var`. Blender workers and future agents use separate system identities and never own the immutable runtime.

**Tech Stack:** Ubuntu 24.04 LTS, Blender 5.2.0 LTS Linux x64, Bash, Python 3.12, Blender Python API, systemd, Git.

## Global Constraints
- Blender release line: 5.2 LTS, initial exact pin 5.2.0.
- Runtime root: `/opt/blender-pro`.
- Durable data root: `/srv/blender-pro`.
- No GPU is currently exposed; qualify CPU rendering now and leave GPU selection auto-detectable.
- Do not edit Traefik, 9router, Obsidian, or their Docker networks/volumes.
- Do not expose Blender MCP or render control on ports 80/443 or any public listener.
- Production rendering must work without an X server.
- Third-party extension updates must be explicit and version pinned.

---

### Task 1: Baseline and isolated control repository
**Files:** Create `/root/blender-pro-control`, `.gitignore`, `docs/superpowers/specs/2026-08-13-blender-pro-vps-design.md`, and this plan under `docs/superpowers/plans/`.
- [ ] Capture OS, CPU, RAM, disk, listeners, Docker container identity/status, and protected-service fingerprints in `baseline/before.txt`.
- [ ] Initialize Git, commit baseline/docs, add ignored `.worktrees/`, create branch/worktree `build/vps-foundation`.
- [ ] Verify the worktree is isolated and clean before deployment changes.

### Task 2: Filesystem and identities
**Files:** Create `deploy/bootstrap.sh` plus `tests/test_layout.py`.
- [ ] RED: test expected runtime/data/cache/log directories and ownership contract.
- [ ] GREEN: create `blender-pro` group plus `blender-admin`, `blender-agent`, `blender-render` system identities and isolated directories.
- [ ] Make `/opt/blender-pro` root-owned and worker-unwritable; make render/cache/log paths writable only where required.

### Task 3: Exact Blender 5.2.0 runtime
**Files:** Create `deploy/install_blender.sh`, `/opt/blender-pro/locks/blender.lock.json`, `/opt/blender-pro/bin/blender-pro`.
- [ ] Download the official 5.2.0 Linux x64 archive and official SHA256 manifest from `download.blender.org`.
- [ ] Verify checksum before extraction; extract side-by-side to `/opt/blender-pro/releases/5.2.0` and atomically point `/opt/blender-pro/current` at it.
- [ ] Verify `Blender 5.2.0 LTS`, hash `fbe6228777e7`, and background startup on this VPS.

### Task 4: Runtime profiles and bundled extensions
**Files:** Create `profiles/render-safe.env`, `profiles/asset-fetch.env`, `skills/blender_pro/runtime/inspect_extensions.py`.
- [ ] RED: integration check must fail until profile wrapper isolates config/scripts/temp/cache paths.
- [ ] GREEN: set isolated Blender environment variables and verify they resolve only inside Blender Pro paths.
- [ ] Inspect Node Wrangler and Rigify availability in the pinned runtime; record exact module/version/package state instead of guessing identifiers.
- [ ] If an extension must be fetched, install it only into the private system extension root and record its archive hash/version.

### Task 5: Headless verification and render worker
**Files:** Create `skills/blender_pro/validation/preflight.py`, `skills/blender_pro/render/preview.py`, `bin/blender-verify`, `bin/blender-preview`, `bin/blender-render`, `bin/blender-job`, and tests.
- [ ] RED: tests reject path escape, missing blend file, missing camera, and output outside `/srv/blender-pro`.
- [ ] GREEN: implement manifest/path validation and Blender-side scene preflight emitting JSON.
- [ ] Generate a deterministic smoke-test `.blend`, run background preflight, preview render, and final CPU render.
- [ ] Use unique job/output/cache directories and nonzero exit codes on verification/render failures.

### Task 6: Asset library contract
**Files:** Create `assets/README.md`, `manifests/schema/project.schema.json`, example manifest, and directory scaffolding.
- [ ] Establish incoming/work/published/linked/catalog roots.
- [ ] Add immutable versioned publishing convention and linked-library path contract.
- [ ] Prove a linked-library smoke scene can open and render headlessly.

### Task 7: Secured agent boundary
**Files:** Create `agent/gateway.py`, `agent/policy.py`, `tests/test_agent_policy.py`, and `bin/blender-agent-mcp`.
- [ ] RED: tests reject arbitrary Python, shell commands, absolute paths outside allowed roots, and public-network bind requests.
- [ ] GREEN: expose only structured actions such as inspect, verify, preview, render, job status, and approved asset operations.
- [ ] Run the MCP/agent bridge over stdio by default under `blender-agent`; do not create a public TCP listener.
- [ ] Keep the Blender render worker a separate process and identity from the agent bridge.

### Task 8: BlenderKit staging policy
**Files:** Create `deploy/install_blenderkit.sh`, `assets/blenderkit-policy.md`, and extension lock metadata.
- [ ] Discover the current approved BlenderKit release from upstream at install time, then pin exact version, commit/tag, archive URL, and SHA256.
- [ ] Install BlenderKit only for the asset-fetch profile; production render profile must not require network access or BlenderKit cache paths.
- [ ] Validate that published assets resolve from `/srv/blender-pro/assets/published` without BlenderKit network access.

### Task 9: systemd worker hardening
**Files:** Create `systemd/blender-pro-render@.service`, optional `systemd/blender-pro-agent.service`, and install script.
- [ ] Apply separate users, private temp, no new privileges, restricted writable paths, and CPU/memory/process safeguards compatible with systemd 255.
- [ ] Do not add Traefik labels, Docker networks, reverse-proxy routes, or public listeners.
- [ ] Start a smoke render through the worker unit and verify cleanup leaves no orphan Blender process.

### Task 10: Before/after acceptance
**Files:** Create `baseline/after.txt`, `reports/acceptance.json`, and `bin/blender-doctor`.
- [ ] Re-capture protected service container IDs/status, listeners, Docker networks, and relevant config checksums.
- [ ] Assert Traefik, 9router, and existing services were not modified by this deployment.
- [ ] Run full foundation tests, Blender version check, extension inspection, preflight, preview, final render, path-security tests, and rollback-symlink test.
- [ ] Commit verified work on `build/vps-foundation`; leave Flamenco disabled until the single-node worker passes acceptance.
