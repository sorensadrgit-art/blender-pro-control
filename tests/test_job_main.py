import sys
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
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


if __name__ == '__main__':
    unittest.main()
