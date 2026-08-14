import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'runtime' / 'agent_server.py'
POLICY = ROOT / 'runtime' / 'agent_policy.py'
UNIT = ROOT / 'systemd' / 'blender-pro-render@.service'
SUDOERS = ROOT / 'deploy' / 'blender-pro-agent.sudoers'
PERMISSIONS = ROOT / 'deploy' / 'configure_direct_agent_permissions.sh'


class DirectAgentContractTests(unittest.TestCase):
    def test_blender_mcp_stays_private_and_bridge_free(self):
        text = SERVER.read_text(encoding='utf-8')
        self.assertNotIn('0.0.0.0', text)
        self.assertNotIn('agent-bridge', text.lower())
        self.assertNotIn('9130', text)

    def test_policy_uses_narrow_render_start_helper(self):
        text = POLICY.read_text(encoding='utf-8')
        self.assertIn('/opt/blender-pro/bin/blender-render-start', text)
        self.assertIn('/usr/bin/sudo', text)
        self.assertNotIn("SYSTEMCTL = '/usr/bin/systemctl'", text)

    def test_direct_agent_permission_sources_exist(self):
        self.assertTrue(SUDOERS.is_file(), SUDOERS)
        self.assertTrue(PERMISSIONS.is_file(), PERMISSIONS)
        sudoers = SUDOERS.read_text(encoding='utf-8')
        permissions = PERMISSIONS.read_text(encoding='utf-8')
        self.assertIn('%blender-pro-agent', sudoers)
        self.assertIn('/opt/blender-pro/bin/blender-render-start', sudoers)
        self.assertIn('blender-pro-agent', permissions)
        self.assertIn('2770', permissions)

    def test_worker_joins_direct_agent_group(self):
        text = UNIT.read_text(encoding='utf-8')
        self.assertIn('SupplementaryGroups=blender-pro-agent', text)
        self.assertIn('root:blender-pro-agent', text)
        self.assertNotIn('root:root /srv/blender-pro/jobs/%i.result.json', text)


if __name__ == '__main__':
    unittest.main()
