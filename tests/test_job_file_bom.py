import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))
from job_file import run_job_file

class Result:
    returncode = 0
    stdout = 'ok'
    stderr = ''

class BomManifestTests(unittest.TestCase):
    def test_accepts_utf8_bom_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root/'projects'; project.mkdir()
            assets = root/'assets'; assets.mkdir()
            previews = root/'previews'; previews.mkdir()
            renders = root/'renders'; renders.mkdir()
            jobs = root/'jobs'; jobs.mkdir()
            scene = project/'scene.blend'; scene.write_bytes(b'blend')
            data = {
                'schema': 1, 'project': 'bom', 'scene': str(scene),
                'engine': 'CYCLES', 'frame': 1, 'resolution': [320, 180],
                'preview_output': str(previews/'frame.png'),
                'render_output': str(renders/'frame.png'),
            }
            manifest = jobs/'bom.json'
            manifest.write_text(json.dumps(data), encoding='utf-8-sig')
            result = run_job_file(
                manifest, (project, assets, previews, renders),
                lambda argv, **kwargs: Result(),
                lambda: {'status': 'ok'}, jobs,
            )
            self.assertEqual(result['status'], 'complete')

if __name__ == '__main__':
    unittest.main()
