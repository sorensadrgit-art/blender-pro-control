import sys
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))

from render_settings import parse_render_args


class RenderSettingsTests(unittest.TestCase):
    def test_parse_valid_args(self):
        settings = parse_render_args([
            '12', '1920', '1080', 'CYCLES',
            '/srv/blender-pro/renders/demo/frame.png',
        ])
        self.assertEqual(settings['frame'], 12)
        self.assertEqual(settings['width'], 1920)
        self.assertEqual(settings['height'], 1080)
        self.assertEqual(settings['engine'], 'CYCLES')
        self.assertEqual(settings['output'], '/srv/blender-pro/renders/demo/frame.png')

    def test_rejects_unknown_engine(self):
        with self.assertRaises(ValueError):
            parse_render_args(['1', '320', '180', 'UNKNOWN_ENGINE', '/tmp/out.png'])

if __name__ == '__main__':
    unittest.main()
