import sys
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

from job_plan import build_job_plan


class JobPlanTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            'scene': '/srv/blender-pro/projects/work/smoke/scene.blend',
            'frame': 1,
            'resolution': [320, 180],
            'engine': 'CYCLES',
            'preview_output': '/srv/blender-pro/previews/smoke/frame_0001.png',
            'render_output': '/srv/blender-pro/renders/smoke/frame_0001.png',
        }

    def test_plan_uses_fixed_blender_scripts_and_argv(self):
        plan = build_job_plan(self.manifest)
        self.assertEqual(plan['preflight'][0], '/opt/blender-pro/bin/blender-pro')
        self.assertIn('/opt/blender-pro/skills/preflight.py', plan['preflight'])
        self.assertIn('/opt/blender-pro/skills/preview.py', plan['preview'])
        self.assertIn('/opt/blender-pro/skills/render_frame.py', plan['final'])
        for argv in plan.values():
            self.assertIsInstance(argv, list)
            self.assertNotIn('/bin/bash', argv)
            self.assertNotIn('/bin/sh', argv)

    def test_plan_carries_manifest_render_settings_only_as_values(self):
        plan = build_job_plan(self.manifest)
        preview = plan['preview']
        final = plan['final']
        self.assertEqual(preview[-5:], ['1', '320', '180', 'CYCLES', self.manifest['preview_output']])
        self.assertEqual(final[-5:], ['1', '320', '180', 'CYCLES', self.manifest['render_output']])


if __name__ == '__main__':
    unittest.main()
