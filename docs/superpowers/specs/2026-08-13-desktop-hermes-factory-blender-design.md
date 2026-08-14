# Hermes Desktop + Factory Desktop Blender Access Design

## Goal
Use Hermes Desktop and Factory Desktop as the only AI clients for Blender Pro, with each connecting independently to the VPS through its own restricted SSH identity.

## Approved topology
Hermes Desktop -> Windows OpenSSH stdio -> dedicated Hermes Blender identity -> private Blender MCP -> policy -> render worker -> Blender 5.2 LTS

Factory Desktop -> Windows OpenSSH stdio -> dedicated Factory Blender identity -> private Blender MCP -> policy -> render worker -> Blender 5.2 LTS

There is no shared agent bridge, public Blender MCP endpoint, shared desktop key, or shared agent process state.

## Preserve
- Keep all existing Hermes Desktop MCP integrations unchanged except for adding `blender-pro`.
- Keep all existing Factory Desktop MCP integrations unchanged except for adding `blender-pro`.
- Keep the existing administrator SSH connection for human administration only.
- Keep Blender Pro, Traefik, 9router, Obsidian, studio-relay, Docker topology, and the existing Blender render security boundary unchanged.

## Separate desktop identities
Create two dedicated VPS identities, one for Hermes Desktop and one for Factory Desktop. Each uses a different Windows-generated SSH key and is authorized only for the Blender MCP transport path.

The desktop Blender identities must not provide a general-purpose VPS shell, SSH forwarding, or broader administrative capabilities. They share only the existing Blender render permission group required by the private MCP policy.

## Windows SSH aliases
Add two new aliases to the existing Windows SSH configuration:
- `blender-hermes` for Hermes Desktop
- `blender-factory` for Factory Desktop

Each alias uses its own key and its own VPS identity. The existing administrator alias remains unchanged and is not referenced by either AI client.

## Hermes Desktop MCP
Add one `blender-pro` stdio MCP entry to Hermes Desktop. The local process is Windows OpenSSH and the target is the `blender-hermes` alias. The server side launches the private Blender MCP automatically.

## Factory Desktop MCP
Add one separate `blender-pro` stdio MCP entry to Factory Desktop. The local process is Windows OpenSSH and the target is the `blender-factory` alias. Factory keeps its existing desktop account, model configuration, and unrelated MCP integrations.

## Migration order
1. Back up Windows Hermes, Factory, and SSH configuration plus relevant VPS state.
2. Create the two restricted VPS identities and dedicated desktop keypairs.
3. Validate raw SSH stdio connectivity for both identities.
4. Add and test Hermes Desktop `blender-pro` MCP.
5. Add and test Factory Desktop `blender-pro` MCP.
6. Run independent Blender smoke renders from both desktop agents.
7. Only after both desktop clients pass, retire the VPS-side Factory and Hermes agent runtimes.
8. Re-run repository tests, Blender doctor, connection restrictions, listener checks, and protected-service health checks.

The current VPS agent runtimes remain available as rollback until both desktop clients pass the complete acceptance sequence.

## VPS runtime retirement
After desktop acceptance, remove the VPS Factory Droid runtime and its Blender-client membership. Retire VPS Hermes backend/gateway/provider-helper services only after confirming no unrelated consumer depends on them.

Preserve the existing Linux Hermes identity unless a filesystem ownership audit proves deletion is safe. Do not remove or restart 9router, Traefik, Obsidian, studio-relay, or unrelated Docker services as part of this migration.

## Error handling and rollback
- Back up both desktop MCP configurations and the Windows SSH configuration before edits.
- Keep the existing administrator SSH alias unchanged.
- Keep VPS agent runtimes available until both desktop smoke tests pass.
- If either desktop MCP fails, roll back only that new MCP entry and its dedicated SSH identity while leaving Blender Pro unchanged.
- Perform VPS runtime retirement only after fresh desktop and Blender verification.

## Acceptance criteria
- Hermes Desktop connects to `blender-pro` through its dedicated identity.
- Factory Desktop connects to `blender-pro` through its dedicated identity.
- Each independently discovers `runtime_status`, `scene_verify`, `job_run`, and `job_status`.
- Each independently passes runtime status, approved scene verification, smoke render submission, and completed job status.
- Hermes and Factory use different SSH keys and different VPS identities.
- Neither desktop Blender identity provides a general-purpose VPS shell.
- No public Blender MCP listener or shared agent bridge exists.
- Existing desktop MCP integrations remain unchanged except for adding `blender-pro`.
- Blender Pro tests and Blender doctor pass after migration.
- Traefik, 9router, Obsidian, studio-relay, and shared Docker networking remain healthy and unchanged.
- The accepted configuration is recorded in the Blender Pro repository with a clean working tree.

## Non-goals
- No desktop-to-desktop delegation between Hermes and Factory.
- No public HTTP/SSE Blender MCP endpoint.
- No shared SSH identity between the two agents.
- No changes to Blender rendering logic, asset policy, or BlenderKit architecture.
- No redesign of unrelated desktop MCP integrations.
- No studio-relay migration in this phase.
