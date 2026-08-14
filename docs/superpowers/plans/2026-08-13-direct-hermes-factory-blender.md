# Direct Hermes + Factory Blender Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect Hermes Agent and Factory Droid independently to Blender Pro through direct local stdio MCP, eliminate obsolete bridge/Skybridge runtime components, and retain the existing hardened Blender worker boundary.

**Architecture:** Both clients run under separate Linux identities and launch `/opt/blender-pro/bin/blender-agent-mcp` as a local subprocess. The MCP remains unprivileged; only a root-owned, slug-validating render-start helper may invoke the protected systemd worker through a narrow sudoers rule. Shared render-control directories move from world-writable to a dedicated `blender-pro-agent` group.

**Tech Stack:** Ubuntu 24.04 LTS, Blender 5.2.0 LTS, Python 3.12, systemd 255, sudoers, Hermes Agent v0.20.0, Factory Droid CLI, MCP stdio, Git.

## Global Constraints
- No shared agent bridge, Skybridge service, broker, TCP MCP listener, or public Blender endpoint.
- Hermes and Factory must run independently and must not call one another.
- Preserve Hermes Basic Memory and Notion MCP entries.
- Preserve Traefik, 9router, Obsidian, studio-relay, and the shared `agent-control` Docker network.
- Do not grant Hermes or Factory unrestricted sudo, shell, or Blender Python through this integration.
- Keep `/opt/blender-pro` root-owned and non-writable by both agents.
- Factory credentials must stay out of Git and must not be printed in logs.

---

### Task 1: Baseline and cleanup dependency gate

**Files:**
- Create: `reports/direct-agents-before.txt`
- Create: `tests/test_direct_agents_contract.py`

**Interfaces:**
- Consumes: current VPS services, Docker metadata, Hermes MCP config, Blender runtime.
- Produces: an auditable before-state and static contract tests for the direct-agent topology.
- [ ] **Step 1: Capture the live before-state**

Record current branch/commit, Blender doctor output, Docker containers/networks, protected container IDs, relevant listeners, Hermes version/MCP list, Factory presence, permissions on Blender control directories, and references to `agent-bridge`/Skybridge. Never record credential values.

- [ ] **Step 2: Write the failing topology contract test**

Add assertions that versioned configuration contains no public Blender listener, no `agent-bridge` dependency, retains the existing fixed MCP tool boundary, and defines a direct-agent permission configuration.

- [ ] **Step 3: Run the focused test and confirm RED**

Run: `python3 -m unittest tests.test_direct_agents_contract -v`
Expected: FAIL because the direct-agent permission/install files do not exist yet.

- [ ] **Step 4: Prove cleanup dependencies before deletion**

Inspect `agent-bridge`, `/docker/agent-bridge`, `/opt/agent-bridge`, `/docker/skybridge`, studio-relay runtime environment/config, systemd units, and Docker network membership. Mark each target as removable or preserved; do not delete anything in this task.

- [ ] **Step 5: Commit baseline/test only**

```bash
git add reports/direct-agents-before.txt tests/test_direct_agents_contract.py
git commit -m "test: define direct agent topology contract"
```

### Task 2: Narrow Blender render privilege boundary

**Files:**
- Create: `runtime/render_start_main.py`
- Create: `tests/test_render_start_main.py`
- Modify: `runtime/agent_policy.py`
- Modify: `tests/test_agent_policy.py`
- Create: `deploy/blender-pro-agent.sudoers`

**Interfaces:**
- Consumes: safe job instance slug and existing `blender-pro-render@.service` template.
- Produces: `render_start_main.main(argv)` and `AgentPolicy.job_argv()` using non-interactive sudo to one root-owned helper.
- [ ] **Step 1: Write failing helper tests**

Test that only one instance argument is accepted, only `^[A-Za-z0-9][A-Za-z0-9._-]*$` is allowed, and the helper calls exactly `/usr/bin/systemctl start blender-pro-render@<instance>.service` with `shell=False` semantics.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_render_start_main tests.test_agent_policy -v`
Expected: FAIL because `render_start_main.py` and the new policy command do not exist.

- [ ] **Step 3: Implement the minimal helper**

`render_start_main.py` must return `64` for invalid arguments, `65` for unsafe slugs, and otherwise execute the exact systemctl argv and return its exit code. No shell interpolation is permitted.

- [ ] **Step 4: Change the MCP job command**

Make `AgentPolicy.job_argv()` return exactly:

```python
['/usr/bin/sudo', '-n', '/opt/blender-pro/bin/blender-render-start', manifest.stem]
```

- [ ] **Step 5: Add the scoped sudoers source**

The versioned sudoers fragment must grant only members of `%blender-pro-agent` passwordless execution of `/opt/blender-pro/bin/blender-render-start *` as root. Validate with `visudo -cf` before installation.

- [ ] **Step 6: Run focused and full tests**

Run: `python3 -m unittest tests.test_render_start_main tests.test_agent_policy -v` and `python3 -m unittest discover -s tests -q`.

- [ ] **Step 7: Commit**

```bash
git add runtime/render_start_main.py runtime/agent_policy.py deploy/blender-pro-agent.sudoers tests/test_render_start_main.py tests/test_agent_policy.py
git commit -m "feat: add narrow render start privilege"
```

### Task 3: Replace world-writable render control with group permissions

**Files:**
- Modify: `systemd/blender-pro-render@.service`
- Create: `deploy/configure_direct_agent_permissions.sh`
- Modify: `tests/test_systemd_unit.py`
- Modify: `tests/test_direct_agents_contract.py`

**Interfaces:**
- Consumes: Linux group `blender-pro-agent`, Hermes user, Factory user, render helper from Task 2.
- Produces: group-readable/writable job control and group-readable render results without world-writable directories.
- [ ] **Step 1: Write failing permission/unit tests**

Require `SupplementaryGroups=blender-pro-agent`; require post-run ownership to `root:blender-pro-agent`; reject `1777`/world-write assumptions in versioned deployment configuration.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_systemd_unit tests.test_direct_agents_contract -v`
Expected: FAIL on the new group/ownership requirements.

- [ ] **Step 3: Implement idempotent permission configuration**

The deployment script must create `blender-pro-agent` if absent, add `hermes` to that group when present, set `/srv/blender-pro/jobs`, `/srv/blender-pro/previews`, and `/srv/blender-pro/renders` to `root:blender-pro-agent` mode `2770`, and normalize existing manifests/results/outputs to group-readable modes without making runtime code agent-writable. Factory is added to the group when its separate identity is created in Task 5.

- [ ] **Step 4: Update the systemd worker**

Add `SupplementaryGroups=blender-pro-agent`. Change `ExecStopPost` ownership to `root:blender-pro-agent` and ensure produced result JSON/images are group-readable. Keep all existing sandboxing and network denial directives.

- [ ] **Step 5: Install versioned runtime pieces**

Copy the helper to `/opt/blender-pro/skills/render_start_main.py`, expose `/opt/blender-pro/bin/blender-render-start` as root-owned executable, install the validated sudoers fragment under `/etc/sudoers.d/`, run the permission script, and `systemctl daemon-reload` after replacing the unit symlink/source.

- [ ] **Step 6: Verify non-root render start**

Run the existing `mcp-smoke` or a fresh smoke manifest through the MCP as `hermes`, verify the systemd job completes, and verify Hermes can read the result without root.

- [ ] **Step 7: Commit**

```bash
git add systemd/blender-pro-render@.service deploy/configure_direct_agent_permissions.sh tests/test_systemd_unit.py tests/test_direct_agents_contract.py
git commit -m "feat: harden direct agent render permissions"
```

### Task 4: Direct Hermes Blender MCP

**Files:**
- Runtime config only: `/home/hermes/.hermes/config.yaml` (backup before edit; never commit secrets)
- Create: `reports/hermes-direct-mcp.txt`

**Interfaces:**
- Consumes: `/opt/blender-pro/bin/blender-agent-mcp` and Task 3 permissions.
- Produces: Hermes MCP server named `blender-pro` alongside unchanged `basic-memory` and `notion` entries.

- [ ] **Step 1: Backup and hash Hermes config**

Create a timestamped root-owned backup and record only the config hash plus MCP server names in the report.

- [ ] **Step 2: Add direct stdio MCP**

Prefer the installed CLI if functional:

```bash
hermes mcp add blender-pro --command /opt/blender-pro/bin/blender-agent-mcp
```

Run it in the Hermes service-account context. If this installed Hermes build mishandles `mcp add`, patch only `mcp_servers.blender-pro` in YAML with `command: /opt/blender-pro/bin/blender-agent-mcp` and no bridge URL.
- [ ] **Step 3: Test Hermes MCP connection**

Run `hermes mcp list` and `hermes mcp test blender-pro` as Hermes. Confirm `basic-memory`, `notion`, and `blender-pro` are enabled and no bridge endpoint is referenced.

- [ ] **Step 4: Run independent Blender calls**

From Hermes, call `runtime_status`, then `scene_verify` on `/srv/blender-pro/projects/work/smoke/scene.blend`, then execute/read a smoke render job. Record status and tool names only.

- [ ] **Step 5: Commit report**

```bash
git add reports/hermes-direct-mcp.txt
git commit -m "docs: verify direct Hermes Blender MCP"
```

### Task 5: Independent Factory Droid installation and Blender MCP

**Files:**
- Runtime user/config: `/home/factory`, `/home/factory/.factory/mcp.json`
- Create: `reports/factory-direct-mcp.txt`

**Interfaces:**
- Consumes: official Factory Droid Linux installer, direct Blender MCP executable, Task 3 group permissions.
- Produces: separate `factory` service-account context and user-level MCP server `blender-pro`.

- [ ] **Step 1: Create the Factory identity**

Create `factory` with its own home and shell, add it only to `blender-pro-agent`, and do not reuse Hermes home, credentials, or config.

- [ ] **Step 2: Install Droid from Factory's official installer**

Run the current Linux installer in the Factory user context. Verify with `droid --version`. Do not install a bridge or daemon unless required for the CLI itself.

- [ ] **Step 3: Add the stdio MCP as Factory**

```bash
droid mcp add blender-pro /opt/blender-pro/bin/blender-agent-mcp --type stdio
```

Verify `~/.factory/mcp.json` contains a stdio command to that path and contains no secret material.
- [ ] **Step 4: Configure Factory authentication without committing it**

If `FACTORY_API_KEY` is already securely available to the Factory account, use it without printing it. Otherwise leave the CLI installed/configured and mark only the authenticated end-to-end `droid exec` check as blocked on user credential provisioning; never invent or expose a key.

- [ ] **Step 5: Verify Factory MCP**

Run `droid mcp list` as Factory. When authenticated, use Droid to call `runtime_status`, `scene_verify`, and a smoke render independently of Hermes.

- [ ] **Step 6: Commit verification report**

```bash
git add reports/factory-direct-mcp.txt
git commit -m "docs: verify independent Factory Blender MCP"
```

### Task 6: Remove obsolete bridges and Skybridge remnants

**Files:**
- Create: `reports/direct-agents-cleanup.txt`
- Remove live/runtime artifacts only after Task 1 dependency gate marks them removable.

**Interfaces:**
- Consumes: Task 1 dependency inventory and proven direct Hermes/Factory paths.
- Produces: no running `agent-bridge`, no obsolete agent-bridge deployment tree, no unused Skybridge deployment remnants.

- [ ] **Step 1: Re-check protected services immediately before deletion**

Capture container IDs/status for Traefik, 9router, Obsidian, and studio-relay; capture `agent-control` members and studio-relay health.

- [ ] **Step 2: Remove the old agent-bridge deployment**

Use its Compose project to stop/remove only the `agent-bridge` container. Remove its image only if no remaining container uses it. Remove `/docker/agent-bridge` and `/opt/agent-bridge` after the container is gone.

- [ ] **Step 3: Remove proven-unused Skybridge remnants**

Remove `/docker/skybridge` and other bridge-only remnants only if the dependency inventory shows no live consumer. Preserve the shared `agent-control` network and any studio-relay configuration that is independently required.

- [ ] **Step 4: Remove obsolete bridge-era Hermes helper backups/scripts**

Delete only files proven unrelated to current Hermes startup/provider/Basic Memory/Notion. Preserve active `/usr/local/bin/hermes`, Hermes systemd units, Headroom/9router provider path, and current Hermes config backups needed for rollback.
- [ ] **Step 5: Verify cleanup**

Confirm no `agent-bridge` container/listener remains, `/opt/agent-bridge` and `/docker/agent-bridge` are absent, approved Skybridge remnants are absent, and protected services retain their pre-cleanup IDs/status wherever restart was not required.

- [ ] **Step 6: Commit cleanup report**

```bash
git add reports/direct-agents-cleanup.txt
git commit -m "docs: record obsolete bridge cleanup"
```

### Task 7: Full acceptance, merge, and push

**Files:**
- Create: `reports/direct-agents-acceptance.json`
- Modify if necessary: `runtime/doctor.py`, `tests/test_doctor.py` only to add direct-agent checks that are stable and non-secret.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: verified direct-agent production checkpoint on `main` and GitHub.

- [ ] **Step 1: Run repository verification**

Run `python3 -m unittest discover -s tests -q`, `systemd-analyze verify systemd/blender-pro-render@.service`, `visudo -cf deploy/blender-pro-agent.sudoers`, `git diff --check`, and `/opt/blender-pro/bin/blender-doctor`.

- [ ] **Step 2: Run client acceptance**

Hermes: verify `basic-memory`, `notion`, `blender-pro`; call Blender runtime status, scene verify, smoke render, and result read as non-root.

Factory: verify independent `blender-pro` MCP configuration and, when authenticated, execute the same Blender checks as non-root. If Factory authentication is the only unresolved external dependency, record that exact limitation without weakening permissions or using Hermes credentials.

- [ ] **Step 3: Verify infrastructure isolation**

Confirm no new public Blender listener; `agent-bridge` is absent; `agent-control` remains; studio-relay, Traefik, 9router, and Obsidian are healthy; Hermes gateway/provider integrations remain healthy.

- [ ] **Step 4: Write acceptance JSON**

Record pass/fail for tests, doctor, Hermes direct MCP, Factory installation/config/auth state, render permission boundary, bridge cleanup, public-listener check, and protected services. Include no secrets.

- [ ] **Step 5: Final commit and push feature branch**

```bash
git add reports/direct-agents-acceptance.json runtime/doctor.py tests/test_doctor.py
if ! git diff --cached --quiet; then git commit -m "docs: accept direct Hermes and Factory Blender access"; fi
git push -u origin build/direct-hermes-factory
```

- [ ] **Step 6: Merge only after fresh verification**

Fast-forward `main` only if the feature branch is clean and all non-external acceptance checks pass. Push `main`, then confirm local and GitHub commit hashes match.

## Official references
- Hermes MCP client/config: `https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md`
- Hermes MCP CLI: `https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/cli-commands.md`
- Factory Droid install: `https://docs.factory.ai/droid-cli/quickstart`
- Factory MCP configuration: `https://docs.factory.ai/harness/mcp`
- Factory headless authentication: `https://docs.factory.ai/droid-exec/overview`
