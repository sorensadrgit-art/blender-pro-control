#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
import sys
sys.path.insert(0, '/opt/blender-pro/agent/vendor')

from mcp.server import MCPServer

from agent_policy import AgentPolicy

mcp = MCPServer(
    name='Blender Pro Agent',
    description='Structured Blender VPS controls with no arbitrary code execution.',
    instructions='Use only approved scene verification and manifest job operations.',
    version='1.0.0',
)
policy = AgentPolicy()

LOCK_ROOT = Path('/opt/blender-pro/locks')
CAPABILITIES = Path('/var/lib/blender-pro/state/capabilities.json')


def _read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _run(argv, timeout):
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )
    return {
        'exit_code': completed.returncode,
        'stdout': completed.stdout,
        'stderr': completed.stderr,
    }


@mcp.tool()
def runtime_status() -> dict:
    """Return pinned Blender, extension, and qualified hardware state."""
    return {
        'blender': _read_json(LOCK_ROOT / 'blender.lock.json'),
        'extensions': _read_json(LOCK_ROOT / 'extensions.lock.json'),
        'capabilities': _read_json(CAPABILITIES),
    }


@mcp.tool()
def scene_verify(scene: str) -> dict:
    """Preflight an approved Blender scene without changing it."""
    return _run(policy.verify_argv(scene), timeout=120)


@mcp.tool()
def job_run(manifest: str) -> dict:
    """Run an existing approved render manifest."""
    execution = _run(policy.job_argv(manifest), timeout=7500)
    result_path = Path(policy.result_path(manifest))
    result = None
    if result_path.is_file():
        result = _read_json(result_path)
    return {
        'execution': execution,
        'result': result,
    }


@mcp.tool()
def job_status(manifest: str) -> dict:
    """Read the structured result for an approved render manifest."""
    result_path = Path(policy.result_path(manifest))
    if not result_path.is_file():
        return {'status': 'not_run', 'result_path': str(result_path)}
    return _read_json(result_path)


def main():
    mcp.run()


if __name__ == '__main__':
    main()
