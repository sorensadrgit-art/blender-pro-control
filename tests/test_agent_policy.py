import sys
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))

from agent_policy import AgentPolicy


class AgentPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = AgentPolicy()

    def test_scene_is_confined(self):
        scene = self.policy.scene_path('/srv/blender-pro/projects/work/smoke/scene.blend')
        self.assertEqual(scene, '/srv/blender-pro/projects/work/smoke/scene.blend')
        with self.assertRaises(ValueError):
            self.policy.scene_path('/var/tmp/not-allowed.blend')

    def test_job_is_confined(self):
        job = self.policy.job_path('/srv/blender-pro/jobs/smoke-job.json')
        self.assertEqual(job, '/srv/blender-pro/jobs/smoke-job.json')
        with self.assertRaises(ValueError):
            self.policy.job_path('/var/tmp/not-allowed.json')

    def test_fixed_commands_only(self):
        verify = self.policy.verify_argv('/srv/blender-pro/projects/work/smoke/scene.blend')
        self.assertEqual(verify[0], '/opt/blender-pro/bin/blender-verify')
        self.assertEqual(len(verify), 2)
        run = self.policy.job_argv('/srv/blender-pro/jobs/smoke-job.json')
        self.assertEqual(run, [
            '/usr/bin/systemctl',
            'start',
            'blender-pro-render@smoke-job.service',
        ])

    def test_result_path_is_derived(self):
        result = self.policy.result_path('/srv/blender-pro/jobs/smoke-job.json')
        self.assertEqual(result, '/srv/blender-pro/jobs/smoke-job.result.json')


if __name__ == '__main__':
    unittest.main()
