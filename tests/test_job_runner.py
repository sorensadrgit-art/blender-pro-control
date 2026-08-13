import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))

from job_runner import execute_job


class Result:
    def __init__(self, code=0, out='ok', err=''):
        self.returncode = code
        self.stdout = out
        self.stderr = err


class JobRunnerTests(unittest.TestCase):
    def make_manifest(self, root):
        project = root / 'projects'
        assets = root / 'assets'
        previews = root / 'previews'
        renders = root / 'renders'
        for path in (project, assets, previews, renders):
            path.mkdir()
        scene = project / 'scene.blend'
        scene.write_bytes(b'blend')
        data = {
            'schema': 1, 'project': 'demo', 'scene': str(scene),
            'engine': 'CYCLES', 'frame': 1, 'resolution': [320, 180],
            'preview_output': str(previews / 'frame.png'),
            'render_output': str(renders / 'frame.png'),
        }
        return data, (project, assets, previews, renders)

    def test_executes_three_fixed_phases(self):
        with tempfile.TemporaryDirectory() as td:
            data, roots = self.make_manifest(Path(td))
            calls = []
            def executor(argv, **kwargs):
                calls.append((argv, kwargs))
                return Result()
            result = execute_job(data, roots, executor, lambda: {'status': 'ok'})
            self.assertEqual(result['status'], 'complete')
            self.assertEqual([item['phase'] for item in result['phases']], ['preflight', 'preview', 'final'])
            self.assertEqual(len(calls), 3)
            self.assertTrue(all(isinstance(argv, list) for argv, _ in calls))
            self.assertTrue(all('shell' not in kwargs for _, kwargs in calls))

    def test_rejects_when_disk_status_is_reject(self):
        with tempfile.TemporaryDirectory() as td:
            data, roots = self.make_manifest(Path(td))
            calls = []
            with self.assertRaises(RuntimeError):
                execute_job(data, roots, lambda argv, **kwargs: calls.append(argv), lambda: {'status': 'reject'})
            self.assertEqual(calls, [])

    def test_stops_on_failed_phase(self):
        with tempfile.TemporaryDirectory() as td:
            data, roots = self.make_manifest(Path(td))
            calls = []
            def executor(argv, **kwargs):
                calls.append(argv)
                return Result(code=7, err='boom') if len(calls) == 2 else Result()
            result = execute_job(data, roots, executor, lambda: {'status': 'ok'})
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['failed_phase'], 'preview')
            self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
