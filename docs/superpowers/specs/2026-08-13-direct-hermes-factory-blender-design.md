# Direct Hermes + Factory Blender Access Design

## Goal
Connect Hermes Agent and Factory Droid to Blender Pro independently through the existing private stdio MCP, remove obsolete bridge-era components, and preserve unrelated VPS services.

## Approved topology

Hermes Agent -> direct local stdio -> `/opt/blender-pro/bin/blender-agent-mcp` -> Blender Pro policy -> systemd render worker -> Blender 5.2 LTS

Factory Droid -> direct local stdio -> `/opt/blender-pro/bin/blender-agent-mcp` -> Blender Pro policy -> systemd render worker -> Blender 5.2 LTS

Hermes and Factory never call one another and do not share an agent bridge, Skybridge service, broker, TCP MCP listener, or public Blender endpoint.

## Existing state to preserve
- Blender Pro runtime and repository remain the production source of truth.
- Hermes Agent v0.20.0 remains installed unless a compatibility failure requires an explicit upgrade.
- Hermes Basic Memory and Notion MCP entries remain intact.
- Traefik, 9router, Obsidian, studio-relay, and their unrelated configuration remain untouched.
- The external Docker network `agent-control` remains because studio-relay uses it.
- BlenderKit remains restricted to the existing asset-fetch staging profile.

## Components to remove
- Running `agent-bridge` container and its Compose deployment.
- `/opt/agent-bridge` implementation tree and obsolete promotion/archive material.
- `/docker/agent-bridge` deployment configuration.
- Obsolete Skybridge deployment/config remnants that are no longer used by any live service.
- Obsolete bridge-specific Hermes helper scripts/backups only after proving they are not required by current Hermes startup, provider routing, Basic Memory, or Notion.

Do not delete shared Docker networks or unrelated service configuration merely because old bridge components referenced them.

## Hermes integration
Hermes keeps its current account, workspace, provider path, Basic Memory MCP, and Notion MCP.

Add a `blender-pro` local stdio MCP entry that launches the root-owned Blender MCP executable directly. Hermes must not need root shell access to use Blender Pro.

Hermes must be able to:
- query Blender runtime state;
- verify approved `.blend` files;
- submit approved render jobs;
- read structured job results;
- use any additional Blender tools added later only through the same policy boundary.

## Factory integration
Install Factory Droid as a separate client and service-account context, without reusing Hermes home/config directories.

Factory receives its own `blender-pro` stdio MCP configuration pointing at the same root-owned Blender MCP executable. Its configuration and credentials remain independent from Hermes.

Factory and Hermes may target the same approved Blender projects/assets but must create separate MCP sessions and must not share agent process state.

## Blender execution privilege model
The Blender MCP must remain root-owned and non-writable by either agent.

Neither Hermes nor Factory may receive unrestricted sudo, arbitrary shell execution, or arbitrary Blender Python execution solely to render.

Provide the minimum privilege necessary for the MCP to request approved `blender-pro-render@<safe-instance>.service` starts. Prefer a narrowly scoped root-owned launcher/polkit/sudoers rule over running the complete agent as root.

The jobs directory must not remain broadly world-writable once both direct clients are configured. Job creation and result access must be limited to an explicit Blender agent group or equivalent narrow permission boundary.

## Blender MCP policy
Retain the existing fixed-command policy:
- approved scene roots only;
- `.blend` files only for scene verification;
- approved `/srv/blender-pro/jobs` manifest files only;
- safe instance slug enforcement;
- fixed systemd unit naming;
- no arbitrary command, shell, Python, filesystem, or network APIs.

No Blender MCP TCP listener will be created. Each client launches its own stdio MCP process.

## Cleanup safety gates
Before deleting any bridge/Skybridge artifact:
1. enumerate live containers, systemd units, listeners, mounts, and references;
2. verify the target is not required by Hermes, Factory, studio-relay, Traefik, 9router, or Obsidian;
3. capture a before-state record;
4. remove only proven-unused artifacts;
5. verify protected services remain healthy after each destructive phase.

If an artifact has mixed ownership or uncertain dependencies, preserve it and report it rather than deleting speculatively.

## Testing and acceptance
Acceptance requires all of the following:
- existing Blender Pro unit/integration tests pass;
- Blender doctor remains healthy;
- old `agent-bridge` runtime components are no longer active;
- obsolete Skybridge remnants are gone except any item proven required by another live service;
- `agent-control` remains present and studio-relay remains healthy;
- Hermes still starts and retains Basic Memory + Notion MCPs;
- Hermes lists and successfully calls direct `blender-pro` MCP;
- Factory/Droid is installed independently and lists direct `blender-pro` MCP;
- both clients can call `runtime_status` independently;
- both clients can verify an approved smoke `.blend` independently;
- a render submitted through each client reaches the protected systemd worker and returns a structured result;
- neither client runs as root for normal agent operation;
- no new public listener is created for Blender Pro;
- Traefik, 9router, Obsidian, and studio-relay remain unchanged and healthy;
- repository is clean and implementation changes are committed and pushed only after verification.

## Rollback
- Capture Hermes configuration before edits.
- Capture Docker/container metadata for agent-bridge before cleanup.
- Preserve enough metadata to recreate the previous bridge container temporarily if direct-client validation fails.
- Make Blender permission changes through versioned configuration so they can be reverted atomically.
- Do not restore public bridge exposure unless explicitly requested.

## Non-goals
- No shared multi-agent command center in this phase.
- No public HTTP/SSE MCP endpoint.
- No changes to the Blender render engine or asset pipeline beyond permissions required for direct clients.
- No migration of Hermes Basic Memory or Notion integrations.
- No Factory-to-Hermes delegation or shared agent memory.
