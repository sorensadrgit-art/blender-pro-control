import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

import job_main


class JobMainTests(unittest.TestCase):
    def test_usage_without_manifest(self):
        self.assertEqual(job_main.main([]), 64)

    def test_complete_job_returns_zero(self):
        def fake_run(*args, **kwargs):
            return {'status': 'complete'}
        self.assertEqual(job_main.main(['/srv/blender-pro/jobs/demo.json'], run_file=fake_run), 0)

    def test_failed_preview_returns_40(self):
        def fake_run(*args, **kwargs):
            return {'status': 'failed', 'failed_phase': 'preview'}
        self.assertEqual(job_main.main(['/srv/blender-pro/jobs/demo.json'], run_file=fake_run), 40)

    def test_instance_contract_accepts_matching_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'demo.json'
            manifest.write_text(json.dumps({
                'project': 'demo',
                'preview_output': '/srv/blender-pro/previews/demo/preview.png',
                'render_output': '/srv/blender-pro/renders/demo/final.png',
            }), encoding='utf-8')
            def fake_run(*args, **kwargs):
                return {'status': 'complete'}
            self.assertEqual(job_main.main([str(manifest)], run_file=fake_run, instance='demo'), 0)

    def test_instance_contract_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'demo.json'
            manifest.write_text(json.dumps({
                'project': 'other',
                'preview_output': '/srv/blender-pro/previews/demo/preview.png',
                'render_output': '/srv/blender-pro/renders/demo/final.png',
            }), encoding='utf-8')
            self.assertEqual(job_main.main([str(manifest)], instance='demo'), 10)


if __name__ == '__main__':
    unittest.main()
