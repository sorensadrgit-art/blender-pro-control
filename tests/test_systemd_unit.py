import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / 'systemd' / 'blender-pro-render@.service'


class SystemdUnitTests(unittest.TestCase):
    def test_render_unit_hardening_contract(self):
        text = UNIT.read_text(encoding='utf-8')
        required = [
            'DynamicUser=yes',
            'SupplementaryGroups=blender-pro-agent',
            'NoNewPrivileges=yes',
            'ProtectSystem=strict',
            'ProtectHome=yes',
            'PrivateTmp=yes',
            'PrivateDevices=yes',
            'IPAddressDeny=any',
            'RestrictAddressFamilies=AF_UNIX',
            'CapabilityBoundingSet=',
            'CPUQuota=300%',
            'MemoryMax=12G',
            'TasksMax=512',
        ]
        for item in required:
            self.assertIn(item, text)
        self.assertIn(
            'ExecStart=/opt/blender-pro/bin/blender-job /srv/blender-pro/jobs/%i.json',
            text,
        )
        self.assertIn('ExecStartPre=-+/usr/bin/rm -rf /srv/blender-pro/previews/%i', text)
        self.assertIn('ExecStartPre=-+/usr/bin/rm -rf /srv/blender-pro/renders/%i', text)
        self.assertIn('ExecStartPre=-+/usr/bin/rm -f /srv/blender-pro/jobs/%i.result.json', text)
        self.assertIn('root:blender-pro-agent /srv/blender-pro/jobs/%i.result.json', text)
        self.assertIn('root:blender-pro-agent /srv/blender-pro/previews/%i', text)
        self.assertIn('root:blender-pro-agent /srv/blender-pro/renders/%i', text)
        self.assertIn('/usr/bin/chmod -R g+rX /srv/blender-pro/previews/%i', text)
        self.assertIn('/usr/bin/chmod -R g+rX /srv/blender-pro/renders/%i', text)
        self.assertIn('/usr/bin/chmod g+r /srv/blender-pro/jobs/%i.result.json', text)
        self.assertNotIn('root:root /srv/blender-pro/jobs/%i.result.json', text)
        self.assertNotIn('traefik', text.lower())
        self.assertNotIn('0.0.0.0', text)


if __name__ == '__main__':
    unittest.main()
