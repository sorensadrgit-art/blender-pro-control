# Hermes Desktop + Factory Desktop Blender Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Hermes Desktop and Factory Desktop the only AI clients for Blender Pro, each using its own restricted SSH identity to the private stdio MCP, then retire the VPS-side agent runtimes only after both desktop clients pass full Blender acceptance.

**Architecture:** Windows Hermes and Factory each launch Windows OpenSSH as their MCP subprocess. The VPS maps each desktop key to a different non-root account restricted to `/opt/blender-pro/bin/blender-agent-mcp`; both accounts share only the existing `blender-pro-agent` render group. Blender policy, systemd rendering, projects/assets, Traefik, 9router, Obsidian, studio-relay, and Docker topology remain unchanged.

**Tech Stack:** Windows OpenSSH, PowerShell, Hermes Agent v0.20.0, Factory Droid v0.188.0, Ubuntu 24.04 LTS, OpenSSH server, Bash, Python 3.12, FastMCP stdio, systemd, Blender 5.2.0 LTS, Git.

## Global Constraints
- Preserve every existing Hermes Desktop MCP integration except adding `blender-pro`.
- Preserve every existing Factory Desktop MCP integration except adding `blender-pro`.
- Preserve the human administrator SSH alias `soren`; neither AI client may use it.
- Hermes and Factory must use different Ed25519 keys and different VPS identities.
- Desktop Blender identities must not provide a general shell, forwarding, PTY access, or root access.
- Preserve Blender Pro, Traefik, 9router, Obsidian, studio-relay, Docker topology, `agent-control`, and the current render policy.
- Keep VPS Hermes/Factory runtimes intact until both desktop agents pass end-to-end Blender smoke renders.
- Do not introduce a public Blender MCP listener, shared bridge, or shared desktop identity.
- Never commit private keys, OAuth tokens, bearer tokens, or agent credentials.

---

### Task 1: Baseline and migration contract

**Files:**
- Create: `reports/desktop-clients-before.txt`
- Create: `tests/test_desktop_clients_contract.py`

**Interfaces:**
- Consumes: current desktop config hashes/server names and current VPS service/account state.
- Produces: secret-free before-state and RED tests for the target deployment sources.

- [ ] **Step 1: Capture the before-state**

Record SHA-256 hashes and MCP server names only for:
`C:\Users\soren\AppData\Local\hermes\config.yaml`, `C:\Users\soren\.factory\mcp.json`, and `C:\Users\soren\.ssh\config`.
Also record desktop versions, `ssh -G soren` user/host summary, VPS `hermes`/`factory` account status, `blender-pro-agent` membership, active Hermes-related services, protected container IDs/status, Blender doctor status, and Git commit. Redact token-bearing URLs and secrets.

- [ ] **Step 2: Write the failing contract test**

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSH_SETUP = ROOT / 'deploy' / 'configure_desktop_mcp_ssh.sh'
SSH_CONFIG = ROOT / 'deploy' / 'desktop-blender-ssh-config.txt'
PERMISSIONS = ROOT / 'deploy' / 'configure_direct_agent_permissions.sh'

class DesktopClientContractTests(unittest.TestCase):
    def test_restricted_ssh_sources_exist(self):
        self.assertTrue(SSH_SETUP.is_file(), SSH_SETUP)
        self.assertTrue(SSH_CONFIG.is_file(), SSH_CONFIG)

    def test_distinct_desktop_identities_are_versioned(self):
        text = SSH_SETUP.read_text(encoding='utf-8')
        self.assertIn('blender-hermes', text)
        self.assertIn('blender-factory', text)

    def test_private_mcp_is_forced_and_restricted(self):
        text = SSH_SETUP.read_text(encoding='utf-8')
        self.assertIn('/opt/blender-pro/bin/blender-agent-mcp', text)
        self.assertIn('restrict,command=', text)

    def test_permissions_target_desktop_identities(self):
        text = PERMISSIONS.read_text(encoding='utf-8')
        self.assertIn('blender-hermes', text)
        self.assertIn('blender-factory', text)
        self.assertNotIn('usermod -a -G "$GROUP" hermes', text)
```

- [ ] **Step 3: Verify RED**

```bash
python3 -m unittest tests.test_desktop_clients_contract -v
```

Expected: FAIL because the desktop deployment sources do not exist and the permissions script still targets VPS Hermes.

- [ ] **Step 4: Commit**

```bash
git add reports/desktop-clients-before.txt tests/test_desktop_clients_contract.py
git commit -m "test: define desktop Blender client contract"
```

### Task 2: Version the restricted SSH deployment

**Files:**
- Create: `deploy/configure_desktop_mcp_ssh.sh`
- Create: `deploy/desktop-blender-ssh-config.txt`
- Modify: `deploy/configure_direct_agent_permissions.sh`
- Test: `tests/test_desktop_clients_contract.py`

**Interfaces:**
- Consumes: two Ed25519 public-key file paths and existing `blender-pro-agent` group.
- Produces: password-locked `blender-hermes` and `blender-factory` accounts restricted to the Blender MCP plus a Windows alias template.

- [ ] **Step 1: Implement `configure_desktop_mcp_ssh.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 HERMES_PUBKEY FACTORY_PUBKEY" >&2
  exit 64
fi

GROUP=blender-pro-agent
MCP=/opt/blender-pro/bin/blender-agent-mcp

provision() {
  local user="$1" keyfile="$2" key auth
  [[ -r "$keyfile" ]] || { echo "missing public key: $keyfile" >&2; return 66; }
  /usr/bin/ssh-keygen -l -f "$keyfile" | /usr/bin/grep -q ED25519 || {
    echo "public key must be ED25519: $keyfile" >&2
    return 65
  }
  key="$(/usr/bin/tr -d '\r\n' < "$keyfile")"

  if ! id "$user" >/dev/null 2>&1; then
    /usr/sbin/useradd --system --create-home --user-group \
      --home-dir "/home/$user" --shell /bin/bash "$user"
  fi
  /usr/bin/passwd -l "$user" >/dev/null
  /usr/sbin/usermod -a -G "$GROUP" "$user"

  /usr/bin/install -d -o root -g root -m 0755 "/home/$user"
  /usr/bin/install -d -o root -g root -m 0755 "/home/$user/.ssh"
  auth="/home/$user/.ssh/authorized_keys"
  /usr/bin/printf 'restrict,command="%s" %s\n' "$MCP" "$key" > "$auth"
  /usr/bin/chown root:root "$auth"
  /usr/bin/chmod 0644 "$auth"
}

provision blender-hermes "$1"
provision blender-factory "$2"
```

- [ ] **Step 2: Add the Windows SSH alias template**

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

- [ ] **Step 3: Update future render-group membership**

Replace the old Hermes-only membership block in `deploy/configure_direct_agent_permissions.sh` with:

```bash
for user in blender-hermes blender-factory; do
  if id "$user" >/dev/null 2>&1; then
    usermod -a -G "$GROUP" "$user"
  fi
done
```

- [ ] **Step 4: Verify GREEN**

```bash
python3 -m unittest tests.test_desktop_clients_contract -v
bash -n deploy/configure_desktop_mcp_ssh.sh
bash -n deploy/configure_direct_agent_permissions.sh
python3 -m unittest discover -s tests -q
```

- [ ] **Step 5: Commit**

```bash
git add deploy/configure_desktop_mcp_ssh.sh deploy/desktop-blender-ssh-config.txt deploy/configure_direct_agent_permissions.sh tests/test_desktop_clients_contract.py
git commit -m "feat: add restricted desktop Blender identities"
```

### Task 3: Generate keys, deploy identities, and add Windows aliases

**Files:**
- Runtime only: `C:\Users\soren\.ssh\blender_hermes_ed25519{,.pub}`
- Runtime only: `C:\Users\soren\.ssh\blender_factory_ed25519{,.pub}`
- Modify runtime only: `C:\Users\soren\.ssh\config`
- Create: `reports/desktop-ssh-identities.txt`

**Interfaces:**
- Consumes: Task 2 script and human-admin alias `soren` for deployment only.
- Produces: two different non-root desktop transport aliases.

- [ ] **Step 1: Back up desktop configs**

Create `C:\Users\soren\.backups\blender-desktop-migration\<timestamp>\` and copy Hermes config, Factory MCP config, and SSH config. Record hashes only.

- [ ] **Step 2: Generate separate keys only if the target files are absent**

```powershell
$sshKeygen = "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe"
& $sshKeygen -t ed25519 -f "$env:USERPROFILE\.ssh\blender_hermes_ed25519" -N "" -C "blender-hermes-desktop"
& $sshKeygen -t ed25519 -f "$env:USERPROFILE\.ssh\blender_factory_ed25519" -N "" -C "blender-factory-desktop"
& $sshKeygen -lf "$env:USERPROFILE\.ssh\blender_hermes_ed25519.pub"
& $sshKeygen -lf "$env:USERPROFILE\.ssh\blender_factory_ed25519.pub"
```

Verify the fingerprints differ. Stop rather than overwrite any existing key.

- [ ] **Step 3: Transfer public keys only and provision the VPS identities**

Use the existing `soren` administrator path to copy only the `.pub` files to a temporary root-only location, run the versioned Task 2 script with those two public-key paths, then remove the temporary copies.

Verify:

```bash
id blender-hermes
id blender-factory
getent group blender-pro-agent
```

- [ ] **Step 4: Append aliases without changing `Host soren`**

Append the Task 2 template only if `Host blender-hermes` and `Host blender-factory` are absent.

- [ ] **Step 5: Verify resolved client settings**

```powershell
ssh -G blender-hermes
ssh -G blender-factory
```

Expected: different `user` and `identityfile` values; neither user is root.

- [ ] **Step 6: Verify the transport restriction**

Close stdin while connecting to each alias and confirm the MCP transport exits without presenting an interactive shell. Supply a harmless remote command with stdin closed and verify that command is not executed because the server-side forced Blender MCP command takes precedence.

- [ ] **Step 7: Commit the report**

```bash
git add reports/desktop-ssh-identities.txt
git commit -m "docs: verify separate desktop SSH identities"
```

### Task 4: Connect and accept Hermes Desktop

**Files:**
- Modify runtime only: `C:\Users\soren\AppData\Local\hermes\config.yaml`
- Create: `reports/hermes-desktop-mcp.txt`

**Interfaces:**
- Consumes: `blender-hermes` alias.
- Produces: Hermes Desktop `blender-pro` MCP and a completed agent smoke render.

- [ ] **Step 1: Snapshot current Hermes server names and config hash**

Record names/hashes only; do not record token-bearing URLs or headers.

- [ ] **Step 2: Add the MCP with Hermes CLI**

```powershell
hermes mcp add blender-pro --command "C:\Windows\System32\OpenSSH\ssh.exe" --args -T blender-hermes
```

Enable all four discovered Blender tools.

- [ ] **Step 3: Verify MCP connectivity**

```powershell
hermes mcp list
hermes mcp test blender-pro
```

Expected tools: `runtime_status`, `scene_verify`, `job_run`, `job_status` only.

- [ ] **Step 4: Verify existing Hermes MCP names are unchanged**

Post-edit set must equal pre-edit set plus exactly `blender-pro`.

- [ ] **Step 5: Create the Hermes smoke manifest**

Create `/srv/blender-pro/jobs/desktop-hermes-smoke.json` through the human-admin VPS connection using project `desktop-hermes-smoke`, scene `/srv/blender-pro/projects/work/smoke/scene.blend`, CYCLES, frame 1, resolution 320x180, and matching preview/render output paths.

- [ ] **Step 6: Run Hermes agent acceptance**

Use a Hermes one-shot prompt that says: use only `blender-pro`; call runtime status; verify the smoke scene; run `desktop-hermes-smoke.json`; read final status. Expected final status: `complete`.

- [ ] **Step 7: Commit report**

```bash
git add reports/hermes-desktop-mcp.txt
git commit -m "docs: verify Hermes Desktop Blender MCP"
```

### Task 5: Connect and accept Factory Desktop

**Files:**
- Modify runtime only: `C:\Users\soren\.factory\mcp.json`
- Create: `reports/factory-desktop-mcp.txt`

**Interfaces:**
- Consumes: `blender-factory` alias and Factory Desktop's existing account/model entitlement.
- Produces: Factory Desktop `blender-pro` MCP and completed agent smoke render.

- [ ] **Step 1: Snapshot Factory server names and config hash**

Record names/hashes only.

- [ ] **Step 2: Add exactly one JSON MCP entry**

Use PowerShell JSON parsing and stop if `blender-pro` already exists. Add:

```json
{
  "type": "stdio",
  "command": "C:\\Windows\\System32\\OpenSSH\\ssh.exe",
  "args": ["-T", "blender-factory"],
  "disabled": false
}
```

Write with sufficient JSON depth to preserve all existing nested entries.

- [ ] **Step 3: Verify MCP connectivity and preservation**

```powershell
droid mcp list
```

Expected: `blender-pro` is connected at user scope; post-edit server-name set equals pre-edit set plus exactly `blender-pro`.

- [ ] **Step 4: Verify Factory model entitlement before retirement**

Run a minimal read-only `droid exec`. If authentication, subscription, or model entitlement fails, STOP and keep all VPS agent runtimes intact.

- [ ] **Step 5: Create the Factory smoke manifest**

Create `/srv/blender-pro/jobs/desktop-factory-smoke.json` with project `desktop-factory-smoke`, the approved smoke scene, CYCLES, frame 1, 320x180 resolution, and matching preview/render paths.

- [ ] **Step 6: Run Factory agent acceptance**

Run `droid exec` with a prompt that says: use only `blender-pro`; call runtime status; verify the smoke scene; run `desktop-factory-smoke.json`; read final status. Expected final status: `complete`.

- [ ] **Step 7: Commit report**

```bash
git add reports/factory-desktop-mcp.txt
git commit -m "docs: verify Factory Desktop Blender MCP"
```

### Task 6: Retire VPS Hermes/Factory runtimes only after both desktop passes

**Files:**
- Create: `reports/vps-agent-retirement.txt`
- Runtime-only VPS service/user cleanup.

**Interfaces:**
- Consumes: Task 4 and Task 5 PASS reports.
- Produces: desktop-only AI clients while preserving Blender and unrelated services.

- [ ] **Step 1: Enforce the retirement gate**

Both desktop reports must show MCP connected and agent-level smoke status `complete`; otherwise STOP.

- [ ] **Step 2: Capture rollback state and dependency evidence**

Record protected container IDs/status, Blender doctor, listeners, Hermes-related unit states, and runtime paths. Create a root-only archive of VPS Hermes/Factory configuration before removal. Recheck that no unrelated service consumes Hermes backend/gateway/Headroom listeners.

- [ ] **Step 3: Retire Factory VPS runtime**

After backup, remove the VPS Droid runtime/config and remove `factory` from `blender-pro-agent`. Audit UID-owned files outside `/home/factory`; delete the account only if that audit proves it is project-only, otherwise lock/preserve it and record the reason.

- [ ] **Step 4: Retire Hermes VPS runtime**

After the dependency check, stop/disable `hermes-backend.service`, `hermes-gateway.service`, `headroom-proxy.service`, and the associated watchdog/timer runtime. Remove the backed-up Hermes agent runtime files and remove `hermes` from `blender-pro-agent`. Preserve the Linux `hermes` UID/account unless a filesystem ownership audit proves deletion safe.

- [ ] **Step 5: Verify only desktop Blender identities remain required**

```bash
getent group blender-pro-agent
systemctl is-active hermes-backend.service hermes-gateway.service headroom-proxy.service || true
```

Expected: `blender-hermes` and `blender-factory` are present; retired agent services are inactive; unrelated services were not restarted.

- [ ] **Step 6: Commit report**

```bash
git add reports/vps-agent-retirement.txt
git commit -m "docs: record VPS agent runtime retirement"
```

### Task 7: Final acceptance

**Files:**
- Create: `reports/desktop-agents-acceptance.json`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: auditable desktop-only production checkpoint.

- [ ] **Step 1: Run repository/Blender verification**

```bash
python3 -m unittest discover -s tests -q
systemd-analyze verify systemd/blender-pro-render@.service
visudo -cf deploy/blender-pro-agent.sudoers
git diff --check
/opt/blender-pro/bin/blender-doctor
```

- [ ] **Step 2: Re-run both desktop agent smoke workflows**

Hermes: `hermes mcp test blender-pro` plus the Hermes smoke prompt. Factory: `droid mcp list` plus the Factory smoke prompt. Both final job statuses must be `complete`.

- [ ] **Step 3: Verify identity isolation and no bridge/public listener**

Confirm distinct alias users, distinct key fingerprints, neither user root, no interactive shell path, no public Blender MCP listener, and no shared agent bridge.

- [ ] **Step 4: Verify desktop config preservation**

Each current desktop MCP server-name set must equal its Task 1 set plus exactly `blender-pro`.

- [ ] **Step 5: Verify protected services**

Traefik, 9router, studio-relay, Obsidian if present, shared Docker networking, and Blender must be healthy. Compare protected container IDs when no restart was expected.

- [ ] **Step 6: Write and commit acceptance JSON**

Record pass/fail for tests, doctor, both desktop MCPs, both renders, SSH separation, VPS retirement, listener/bridge checks, and protected services. Include no secrets.

```bash
git add reports/desktop-agents-acceptance.json
git commit -m "docs: accept desktop Hermes and Factory Blender access"
```

### Task 8: Integrate through the branch-finishing workflow

**Files:**
- No functional files; Git integration only.

**Interfaces:**
- Consumes: clean verified migration branch.
- Produces: user-selected merge/push/keep result.

- [ ] **Step 1: Re-run Task 7 verification on the final branch tip**

Require a clean `git status --short`.

- [ ] **Step 2: Handle the duplicate untracked local spec safely**

Verify the canonical committed spec exists on the migration branch, then remove/archive only the duplicate untracked local copy that would block integration.

- [ ] **Step 3: Invoke `superpowers:finishing-a-development-branch`**

Present the standard three integration options and execute only the user's choice. Re-run the full test suite on any merged result before branch/worktree cleanup.
