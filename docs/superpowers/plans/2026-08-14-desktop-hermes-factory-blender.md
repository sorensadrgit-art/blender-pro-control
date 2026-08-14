# Hermes Desktop + Factory Desktop Blender Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Hermes Desktop and Factory Desktop the only AI clients for Blender Pro, each using its own restricted SSH identity to the private stdio MCP, then retire the VPS-side agent runtimes only after both desktop clients pass full Blender acceptance.

**Architecture:** Windows Hermes and Factory each launch Windows OpenSSH as their local MCP subprocess. The VPS authenticates each client with a different Ed25519 key and maps it to a dedicated non-root account that is restricted to the Blender MCP transport path and the existing `blender-pro-agent` render group. The existing Blender policy, render-start sudo boundary, systemd worker, projects, assets, and protected infrastructure remain unchanged.

**Tech Stack:** Windows OpenSSH, PowerShell, Hermes Agent v0.20.0, Factory Droid v0.188.0, Ubuntu 24.04 LTS, OpenSSH server, Python 3.12, FastMCP stdio, systemd, Blender 5.2.0 LTS, Git.

## Global Constraints
- Keep all existing Hermes Desktop MCP integrations unchanged except for adding `blender-pro`.
- Keep all existing Factory Desktop MCP integrations unchanged except for adding `blender-pro`.
- Keep the existing administrator SSH alias `soren` unchanged and never reference it from either AI client.
- Use different SSH keys and different VPS identities for Hermes and Factory.
- Desktop Blender identities must not provide a general-purpose VPS shell, forwarding, PTY access, or broader administrative capabilities.
- Keep Blender Pro, Traefik, 9router, Obsidian, studio-relay, Docker topology, `agent-control`, and the existing render policy unchanged.
- Do not retire the current VPS Hermes/Factory runtimes until both desktop clients pass end-to-end Blender smoke tests.
- No public Blender MCP listener, shared bridge, or shared desktop identity may be introduced.
- Never commit private SSH keys, OAuth tokens, MCP bearer tokens, or Factory/Hermes credentials.

---

### Task 1: Baseline inventory and migration contract

**Files:**
- Create: `reports/desktop-clients-before.txt`
- Create: `tests/test_desktop_clients_contract.py`

**Interfaces:**
- Consumes: current desktop Hermes/Factory config paths, Windows SSH config, current VPS agent identities/services, and the existing Blender deployment files.
- Produces: a secret-free before-state plus regression tests defining the target identity names and deployment sources.

- [ ] **Step 1: Capture the before-state without secrets**

Record only hashes and server names from:
- `C:\Users\soren\AppData\Local\hermes\config.yaml`
- `C:\Users\soren\.factory\mcp.json`
- `C:\Users\soren\.ssh\config`

Also record Hermes/Factory desktop versions, current MCP server names, `ssh -G soren` user/host summary, VPS `hermes`/`factory` account status, Blender group membership, active Hermes-related services, protected container IDs/status, Blender doctor status, and current Git commit. Do not record URLs containing tokens, API keys, private key material, or environment secrets.

- [ ] **Step 2: Write the failing desktop-client contract test**

Create `tests/test_desktop_clients_contract.py` with four tests:

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSH_SETUP = ROOT / 'deploy' / 'configure_desktop_mcp_ssh.sh'
SSH_CONFIG = ROOT / 'deploy' / 'desktop-blender-ssh-config.txt'
PERMISSIONS = ROOT / 'deploy' / 'configure_direct_agent_permissions.sh'

class DesktopClientContractTests(unittest.TestCase):
    def test_restricted_ssh_deployment_source_exists(self):
        self.assertTrue(SSH_SETUP.is_file(), SSH_SETUP)
        self.assertTrue(SSH_CONFIG.is_file(), SSH_CONFIG)

    def test_distinct_desktop_identities_are_versioned(self):
        text = SSH_SETUP.read_text(encoding='utf-8')
        self.assertIn('blender-hermes', text)
        self.assertIn('blender-factory', text)

    def test_private_blender_mcp_is_the_only_forced_transport(self):
        text = SSH_SETUP.read_text(encoding='utf-8')
        self.assertIn('/opt/blender-pro/bin/blender-agent-mcp', text)
        self.assertIn('restrict', text)

    def test_future_permissions_manage_desktop_identities(self):
        text = PERMISSIONS.read_text(encoding='utf-8')
        self.assertIn('blender-hermes', text)
        self.assertIn('blender-factory', text)
        self.assertNotIn('usermod -a -G "$GROUP" hermes', text)
```

- [ ] **Step 3: Verify RED**

Run:

```bash
python3 -m unittest tests.test_desktop_clients_contract -v
```

Expected: FAIL because the restricted SSH deployment source and desktop aliases do not yet exist and the permissions script still targets the VPS Hermes identity.

- [ ] **Step 4: Commit baseline and RED contract**

```bash
git add reports/desktop-clients-before.txt tests/test_desktop_clients_contract.py
git commit -m "test: define desktop Blender client contract"
```

### Task 2: Version the restricted desktop SSH identity deployment

**Files:**
- Create: `deploy/configure_desktop_mcp_ssh.sh`
- Create: `deploy/desktop-blender-ssh-config.txt`
- Modify: `deploy/configure_direct_agent_permissions.sh`
- Test: `tests/test_desktop_clients_contract.py`

**Interfaces:**
- Consumes: two Ed25519 public-key file paths supplied at deployment time and the existing `blender-pro-agent` group.
- Produces: VPS identities `blender-hermes` and `blender-factory`, each password-locked and authorized only for the private Blender MCP path; versioned Windows SSH alias template.

- [ ] **Step 1: Implement the restricted SSH provisioning script**

`deploy/configure_desktop_mcp_ssh.sh` must:
- accept exactly two arguments: Hermes public-key file and Factory public-key file;
- reject missing files and non-Ed25519 public keys with nonzero exit codes;
- create `blender-hermes` and `blender-factory` if absent using separate homes and a standard shell required for OpenSSH forced-command execution;
- lock account passwords;
- add both accounts to `blender-pro-agent`;
- install root-owned SSH authorization files so the transport accounts cannot rewrite their own authorization policy;
- restrict each authorized key to `/opt/blender-pro/bin/blender-agent-mcp` and disable forwarding/PTY behavior through OpenSSH key restrictions;
- never copy private key material to the VPS.

The authorization record generated by the script must combine OpenSSH's restrictive key option with a forced command pointing to `/opt/blender-pro/bin/blender-agent-mcp`, followed by the supplied Ed25519 public key.

- [ ] **Step 2: Add the versioned Windows SSH alias template**

Create `deploy/desktop-blender-ssh-config.txt` containing two entries with these exact identity names and key paths:

```text
Host blender-hermes
    HostName 2.24.90.19
    User blender-hermes
    Port 22
    IdentityFile ~/.ssh/blender_hermes_ed25519
    IdentitiesOnly yes
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes

Host blender-factory
    HostName 2.24.90.19
    User blender-factory
    Port 22
    IdentityFile ~/.ssh/blender_factory_ed25519
    IdentitiesOnly yes
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes
```

- [ ] **Step 3: Update the persistent Blender permissions script**

Replace the old direct-client membership logic with:

```bash
for user in blender-hermes blender-factory; do
  if id "$user" >/dev/null 2>&1; then
    usermod -a -G "$GROUP" "$user"
  fi
done
```

Do not add the retiring VPS `hermes` or `factory` agent identities in this deployment script.

- [ ] **Step 4: Verify GREEN and shell syntax**

Run:

```bash
python3 -m unittest tests.test_desktop_clients_contract -v
bash -n deploy/configure_desktop_mcp_ssh.sh
bash -n deploy/configure_direct_agent_permissions.sh
python3 -m unittest discover -s tests -q
```

Expected: desktop contract tests PASS and the complete repository suite remains green.

- [ ] **Step 5: Commit**

```bash
git add deploy/configure_desktop_mcp_ssh.sh deploy/desktop-blender-ssh-config.txt deploy/configure_direct_agent_permissions.sh tests/test_desktop_clients_contract.py
git commit -m "feat: add restricted desktop Blender identities"
```

### Task 3: Create desktop keys, deploy VPS identities, and add Windows SSH aliases

**Files:**
- Runtime only: `C:\Users\soren\.ssh\blender_hermes_ed25519`
- Runtime only: `C:\Users\soren\.ssh\blender_hermes_ed25519.pub`
- Runtime only: `C:\Users\soren\.ssh\blender_factory_ed25519`
- Runtime only: `C:\Users\soren\.ssh\blender_factory_ed25519.pub`
- Modify runtime only: `C:\Users\soren\.ssh\config`
- Create: `reports/desktop-ssh-identities.txt`

**Interfaces:**
- Consumes: Task 2 deployment script and current admin SSH alias `soren` for one-time administration.
- Produces: two distinct non-root transport aliases, `blender-hermes` and `blender-factory`.

- [ ] **Step 1: Back up desktop configs**

Create a timestamped directory under `C:\Users\soren\.backups\blender-desktop-migration\` and copy the current Hermes config, Factory MCP config, and SSH config there. Record SHA-256 hashes only in the report.

- [ ] **Step 2: Generate two keys without overwriting existing files**

In PowerShell, first fail if any target key file already exists. Then generate separate Ed25519 keypairs:

```powershell
& $env:WINDIR\System32\OpenSSH\ssh-keygen.exe -t ed25519 -f "$env:USERPROFILE\.ssh\blender_hermes_ed25519" -N "" -C "blender-hermes-desktop"
& $env:WINDIR\System32\OpenSSH\ssh-keygen.exe -t ed25519 -f "$env:USERPROFILE\.ssh\blender_factory_ed25519" -N "" -C "blender-factory-desktop"
```

Verify the two public-key fingerprints differ.

- [ ] **Step 3: Copy only public keys to a temporary root-only VPS location**

Use the existing human-admin `soren` SSH alias to transfer the two `.pub` files. Never transfer either private key.

- [ ] **Step 4: Run the versioned VPS provisioning script**

Invoke `deploy/configure_desktop_mcp_ssh.sh` with the two temporary public-key paths, then delete the temporary public-key copies after successful installation.

Verify:

```bash
id blender-hermes
id blender-factory
getent group blender-pro-agent
```

Expected: both identities exist, are distinct, are non-root, and are members of `blender-pro-agent`.

- [ ] **Step 5: Append the two aliases without modifying `Host soren`**

Append the exact Task 2 alias template to `C:\Users\soren\.ssh\config` only after checking neither alias already exists.

- [ ] **Step 6: Verify resolved SSH settings and restrictions**

Run:

```powershell
ssh -G blender-hermes
ssh -G blender-factory
```

Verify each resolves to its own user and key file and neither resolves to `User root`.

Then close stdin while connecting to each alias and confirm the connection does not provide a normal interactive shell. Also try supplying a harmless remote command and verify the supplied command is not executed because the server-side Blender MCP transport restriction takes precedence.

- [ ] **Step 7: Commit the secret-free verification report**

```bash
git add reports/desktop-ssh-identities.txt
git commit -m "docs: verify separate desktop SSH identities"
```

### Task 4: Connect Hermes Desktop directly to Blender Pro

**Files:**
- Modify runtime only: `C:\Users\soren\AppData\Local\hermes\config.yaml`
- Create: `reports/hermes-desktop-mcp.txt`

**Interfaces:**
- Consumes: Windows alias `blender-hermes` and the existing private Blender MCP.
- Produces: Hermes Desktop MCP server `blender-pro` without changing any existing Hermes MCP entry.

- [ ] **Step 1: Snapshot Hermes MCP names before editing**

Save the sorted set of current Hermes MCP names and the config SHA-256 to the report. Do not copy server URLs or bearer headers into the report.

- [ ] **Step 2: Add the Hermes stdio MCP with the installed CLI**

Run:

```powershell
hermes mcp add blender-pro --command "C:\Windows\System32\OpenSSH\ssh.exe" --args -T blender-hermes
```

The `--args` option must remain last. When Hermes discovers the server, enable all four Blender tools.

- [ ] **Step 3: Verify Hermes MCP transport**

Run:

```powershell
hermes mcp list
hermes mcp test blender-pro
```

Expected: `blender-pro` connects through stdio and reports exactly four tools: `runtime_status`, `scene_verify`, `job_run`, and `job_status`.

- [ ] **Step 4: Verify no unrelated Hermes MCP was changed**

Compare the post-edit MCP-name set with the pre-edit set plus exactly one new item, `blender-pro`.

- [ ] **Step 5: Create an approved Hermes desktop smoke manifest**

Using the administrator VPS connection, create `/srv/blender-pro/jobs/desktop-hermes-smoke.json` with project `desktop-hermes-smoke`, the approved smoke scene, 320x180 resolution, and output paths under the matching preview/render directories.

- [ ] **Step 6: Run the Hermes Desktop agent acceptance**

Run a Hermes one-shot prompt instructing Hermes to use only the `blender-pro` MCP tools to:
1. call `runtime_status`;
2. verify `/srv/blender-pro/projects/work/smoke/scene.blend`;
3. run `/srv/blender-pro/jobs/desktop-hermes-smoke.json`;
4. read final `job_status`.

Expected: status `complete`, preview and final output files exist, and no terminal/shell tool is needed for the Blender operation.

- [ ] **Step 7: Commit the Hermes report**

```bash
git add reports/hermes-desktop-mcp.txt
git commit -m "docs: verify Hermes Desktop Blender MCP"
```

### Task 5: Connect Factory Desktop directly to Blender Pro

**Files:**
- Modify runtime only: `C:\Users\soren\.factory\mcp.json`
- Create: `reports/factory-desktop-mcp.txt`

**Interfaces:**
- Consumes: Windows alias `blender-factory` and Factory Desktop's existing account/model configuration.
- Produces: separate Factory Desktop MCP server `blender-pro` without changing any existing Factory MCP entry.

- [ ] **Step 1: Snapshot Factory MCP names before editing**

Record the sorted MCP server-name set and config SHA-256 only. Do not copy token-bearing URLs or credentials to the report.

- [ ] **Step 2: Add only the `blender-pro` JSON object**

Use PowerShell JSON parsing to fail if `mcpServers.blender-pro` already exists. Add exactly:

```json
{
  "type": "stdio",
  "command": "C:\\Windows\\System32\\OpenSSH\\ssh.exe",
  "args": ["-T", "blender-factory"],
  "disabled": false
}
```

Write the JSON back with sufficient depth so all existing nested MCP settings survive.

- [ ] **Step 3: Verify Factory MCP connectivity**

Run:

```powershell
droid mcp list
```

Expected: `blender-pro` is `stdio` and `connected` at user scope.

- [ ] **Step 4: Verify no unrelated Factory MCP changed**

Compare the post-edit server-name set with the pre-edit set plus exactly `blender-pro`.

- [ ] **Step 5: Verify Factory model entitlement before touching VPS rollback state**

Run a minimal read-only `droid exec` request. If Factory authentication or subscription/model entitlement fails, STOP here and keep all current VPS agent runtimes intact. Do not proceed to Task 6.

- [ ] **Step 6: Create and run the Factory desktop smoke manifest**

Create `/srv/blender-pro/jobs/desktop-factory-smoke.json` with project `desktop-factory-smoke`, the approved smoke scene, 320x180 resolution, and matching preview/render output paths.

Run `droid exec` with a prompt that instructs Factory to use only `blender-pro` MCP tools for `runtime_status`, scene verification, job run, and final status.

Expected: final job status `complete` and outputs exist under the Factory smoke paths.

- [ ] **Step 7: Commit the Factory report**

```bash
git add reports/factory-desktop-mcp.txt
git commit -m "docs: verify Factory Desktop Blender MCP"
```

### Task 6: Retire the VPS-side Hermes and Factory agent runtimes

**Files:**
- Create: `reports/vps-agent-retirement.txt`
- Runtime-only service/user cleanup on VPS.

**Interfaces:**
- Consumes: successful Task 4 and Task 5 desktop agent reports.
- Produces: Blender VPS with desktop-only agent clients while preserving Blender and unrelated services.

- [ ] **Step 1: Enforce the retirement gate**

Do not continue unless both desktop reports explicitly show MCP connectivity and completed agent-level Blender smoke renders.

- [ ] **Step 2: Capture protected-service and runtime rollback state**

Record current IDs/status for Traefik, 9router, studio-relay, relevant Obsidian runtime if present, Blender doctor, active listeners, Hermes-related units, and hashes/paths of the VPS Hermes/Factory runtime configuration. Archive VPS Hermes/Factory runtime config to a root-only migration backup location before removal.

- [ ] **Step 3: Reconfirm Hermes provider-helper isolation**

Search service definitions and runtime configuration for consumers of the Hermes backend/gateway/Headroom listeners. Proceed only if no unrelated service consumes them.

- [ ] **Step 4: Retire VPS Factory runtime**

Remove Factory Droid's VPS runtime/config after backup, remove the old `factory` identity from `blender-pro-agent`, and audit files owned by the Factory UID outside its home. Delete the account only if that audit proves it is project-only; otherwise lock it and record why it was preserved.

- [ ] **Step 5: Retire VPS Hermes runtime**

Stop and disable the Hermes backend/gateway/provider-helper runtime and associated watchdog/timer units after the dependency check passes. Remove the VPS Hermes agent runtime files after backup and remove `hermes` from `blender-pro-agent`.

Preserve the Linux `hermes` identity/UID unless a full ownership audit proves deletion safe. Do not alter 9router, Traefik, Obsidian, studio-relay, or unrelated Docker services.

- [ ] **Step 6: Verify the desktop identities remain the only Blender client members**

Check `blender-pro-agent` membership and confirm it includes `blender-hermes` and `blender-factory` and no longer depends on VPS Hermes/Factory agent identities.

- [ ] **Step 7: Commit the retirement report**

```bash
git add reports/vps-agent-retirement.txt
git commit -m "docs: record VPS agent runtime retirement"
```

### Task 7: Final acceptance and production checkpoint

**Files:**
- Create: `reports/desktop-agents-acceptance.json`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: final auditable desktop-only Blender Pro production checkpoint.

- [ ] **Step 1: Run repository and Blender verification**

Run:

```bash
python3 -m unittest discover -s tests -q
systemd-analyze verify systemd/blender-pro-render@.service
visudo -cf deploy/blender-pro-agent.sudoers
git diff --check
/opt/blender-pro/bin/blender-doctor
```

Expected: full test suite green, unit/sudoers/diff checks clean, doctor `ok=true`.

- [ ] **Step 2: Re-run Hermes Desktop acceptance**

Verify `hermes mcp test blender-pro`, rerun the desktop Hermes smoke workflow, and confirm final status `complete`.

- [ ] **Step 3: Re-run Factory Desktop acceptance**

Verify `droid mcp list`, rerun the desktop Factory smoke workflow, and confirm final status `complete`.

- [ ] **Step 4: Verify identity isolation**

Confirm:
- Hermes and Factory aliases resolve to different VPS users;
- key fingerprints differ;
- neither alias resolves to root;
- neither identity provides a general-purpose shell;
- no public Blender MCP listener exists;
- no shared agent bridge exists.

- [ ] **Step 5: Verify desktop configuration preservation**

Compare current desktop MCP-name sets to the Task 1 snapshots. Each must equal the original set plus exactly `blender-pro`.

- [ ] **Step 6: Verify protected services**

Confirm Traefik, 9router, studio-relay, Obsidian if present, shared Docker networking, and Blender remain healthy. Compare protected container IDs where no restart was expected.

- [ ] **Step 7: Write acceptance JSON**

Record pass/fail for repository tests, Blender doctor, both desktop MCP transports, both agent smoke renders, SSH identity separation, VPS runtime retirement, listener/bridge checks, and protected services. Include no secrets or private-key material.

- [ ] **Step 8: Commit**

```bash
git add reports/desktop-agents-acceptance.json
git commit -m "docs: accept desktop Hermes and Factory Blender access"
```

### Task 8: Integrate the migration branch

**Files:**
- No new functional files; Git integration only.

**Interfaces:**
- Consumes: clean, verified feature branch.
- Produces: accepted changes integrated into `main` through the finishing-development-branch workflow.

- [ ] **Step 1: Verify branch cleanliness and exact commit**

Run the complete Task 7 verification again on the final branch tip and ensure `git status --short` is empty.

- [ ] **Step 2: Handle the pre-existing local untracked design copy safely**

Before merging into the main checkout, verify the canonical committed spec exists on the migration branch. Remove or archive only the duplicate untracked local spec that would otherwise block the merge; do not discard any committed work.

- [ ] **Step 3: Use `superpowers:finishing-a-development-branch`**

Present the standard merge/push/keep options. Merge or push only according to the user's selected option, then re-run the full test suite on the integrated result before cleaning the worktree/branch.
