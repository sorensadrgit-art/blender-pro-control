import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))
from job_main import _validate_instance

class JobMainBomTests(unittest.TestCase):
    def test_instance_validation_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root/'demo.json'
            data = {
                'project': 'demo',
                'preview_output': '/srv/blender-pro/previews/demo/preview.png',
                'render_output': '/srv/blender-pro/renders/demo/final.png',
            }
            manifest.write_text(json.dumps(data), encoding='utf-8-sig')
            _validate_instance(manifest, 'demo')

if __name__ == '__main__':
    unittest.main()
