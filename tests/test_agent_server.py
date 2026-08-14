import asyncio
import sys
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
VENDOR = Path('/opt/blender-pro/agent/vendor')
sys.path.insert(0, str(VENDOR))
sys.path.insert(0, str(RUNTIME))

import agent_server


class AgentServerTests(unittest.TestCase):
    def test_exact_tool_surface(self):
        tools = asyncio.run(agent_server.mcp.list_tools())
        names = {tool.name for tool in tools}
        self.assertEqual(names, {
            'runtime_status',
            'scene_verify',
            'job_run',
            'job_status',
        })
