import sys
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

import asset_publish_main


class AssetPublishMainTests(unittest.TestCase):
    def test_usage(self):
        self.assertEqual(asset_publish_main.main([]), 64)

    def test_success(self):
        def fake_publish(*args, **kwargs):
            return {'blend': '/srv/blender-pro/assets/published/props/demo/v001/demo.blend'}
        code = asset_publish_main.main(
            ['/tmp/source.blend', 'props', 'demo', 'v001'],
            publish=fake_publish,
        )
        self.assertEqual(code, 0)
