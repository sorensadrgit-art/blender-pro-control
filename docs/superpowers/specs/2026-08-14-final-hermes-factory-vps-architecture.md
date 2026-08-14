# Final Hermes + Factory + VPS Architecture

## Decision
The prior desktop-only migration plan is superseded. VPS Hermes remains an active, persistent service. Factory remains a separate desktop client. No agent bridge or shared Hermes/Factory runtime is used.

## Final topology

### Hermes Desktop (Windows)
- Independent Hermes Desktop runtime on Windows.
- Source/CLI updated to Hermes v0.20.1 at upstream commit `56a41715`.
- Telegram runs from the Windows Hermes gateway and starts from the Windows login item.
- Desktop Notion uses OAuth and remains Desktop-only.
- Desktop Basic Memory remains available directly to Desktop Hermes.
- Blender MCP is stdio over Git OpenSSH using the restricted `blender-hermes` identity.

### VPS Hermes
- Persistent Hermes v0.20.1 at upstream commit `56a41715`.
- systemd-managed backend, gateway, browser, and watchdogs.
- Headroom 0.35.0 is the inference proxy in front of the configured 9router route.
- Basic Memory is connected by MCP.
- Graphify is connected by local stdio MCP and indexes the Hermes checkout.
- Blender MCP runs locally as an unprivileged stdio subprocess.
- VPS gateway intentionally has no messaging platform configured; Telegram belongs to Hermes Desktop.
- Notion is intentionally not duplicated on the VPS.

### Factory Desktop
- Independent Factory runtime and configuration.
- Blender MCP is stdio over Git OpenSSH using `blender-factory` and its own key.
- Factory shares no Hermes process, home, credentials, Telegram bot, or agent state.

## Blender privilege boundary
- `blender-hermes`, `blender-factory`, and the reactivated VPS `hermes` account use the existing `blender-pro-agent` boundary as appropriate.
- The Blender MCP exposes only `runtime_status`, `scene_verify`, `job_run`, and `job_status`.
- Render submission remains behind the narrow `blender-render-start` sudo rule and systemd render worker.
- Published assets are root-owned and group-readable/traversable, not agent-writable (`2750` directories, `0640` files).
- There is no public Blender MCP listener.

## Persistence and recovery
- VPS Hermes/Headroom/browser/backend/gateway services are enabled at boot.
- Windows Hermes gateway has a Startup login item.
- The obsolete VPS-Hermes retirement script is fail-closed with exit 78; its original is preserved as rollback evidence.
- Existing Hermes backups/snapshots and the Blender repository history remain the rollback path.

## Explicit non-goals
- Do not retire VPS Hermes unless the user explicitly reverses this decision.
- Do not merge Factory into Hermes or share their desktop SSH identities.
- Do not configure a second Telegram bot on VPS Hermes.
- Do not duplicate Desktop Notion OAuth on VPS Hermes.
- Do not expose Blender MCP publicly or reintroduce an agent bridge.

## Operations diagnostics to preserve

### VPS Hermes
```bash
sudo -u hermes -H /home/hermes/.local/bin/hermes version
sudo -u hermes -H /home/hermes/.local/bin/hermes update --check
sudo -u hermes -H /home/hermes/.local/bin/hermes mcp test basic-memory
sudo -u hermes -H /home/hermes/.local/bin/hermes mcp test graphify
sudo -u hermes -H /home/hermes/.local/bin/hermes mcp test blender-pro
systemctl status headroom-proxy.service hermes-browser.service hermes-backend.service hermes-gateway.service --no-pager
curl -fsS http://127.0.0.1:8787/readyz
curl -fsS http://127.0.0.1:9222/json/version
journalctl -u hermes-gateway.service -n 100 --no-pager
```

### Windows Hermes Desktop
```powershell
$env:HERMES_HOME="$env:LOCALAPPDATA\hermes"
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" version
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" update --check
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" gateway status
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" mcp test notion
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" mcp test basic-memory
& "$env:LOCALAPPDATA\hermes-cli\bin\hermes.cmd" mcp test blender-pro
Get-Content "$env:LOCALAPPDATA\hermes\gateway_state.json"
```
