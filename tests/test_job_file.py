import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

from job_file import run_job_file


class Result:
    returncode = 0
    stdout = 'ok'
    stderr = ''


class JobFileTests(unittest.TestCase):
    def test_job_file_writes_atomic_result(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root / 'projects'; project.mkdir()
            assets = root / 'assets'; assets.mkdir()
            previews = root / 'previews'; previews.mkdir()
            renders = root / 'renders'; renders.mkdir()
            jobs = root / 'jobs'; jobs.mkdir()
            scene = project / 'scene.blend'; scene.write_bytes(b'blend')
            manifest = {
                'schema': 1, 'project': 'demo', 'scene': str(scene),
                'engine': 'CYCLES', 'frame': 1, 'resolution': [320, 180],
                'preview_output': str(previews / 'frame.png'),
                'render_output': str(renders / 'frame.png'),
            }
            manifest_path = jobs / 'demo.json'
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            calls = []
            result = run_job_file(
                manifest_path,
                (project, assets, previews, renders),
                lambda argv, **kwargs: calls.append(argv) or Result(),
                lambda: {'status': 'ok'},
                jobs,
            )
            self.assertEqual(result['status'], 'complete')
            result_path = jobs / 'demo.result.json'
            self.assertTrue(result_path.is_file())
            saved = json.loads(result_path.read_text(encoding='utf-8'))
            self.assertEqual(saved['status'], 'complete')
            self.assertEqual(len(calls), 3)

    def test_rejects_manifest_outside_job_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            jobs = root / 'jobs'; jobs.mkdir()
            outside = root / 'outside.json'; outside.write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                run_job_file(outside, (root, root, root, root), lambda *a, **k: Result(), lambda: {'status': 'ok'}, jobs)


if __name__ == '__main__':
    unittest.main()
