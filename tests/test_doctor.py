import sys
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))
from doctor import run_doctor

class DoctorTests(unittest.TestCase):
    def test_live_foundation_is_healthy(self):
        result = run_doctor()
        self.assertTrue(result['ok'], result)
        names = {item['name'] for item in result['checks'] if item['ok']}
        required = {
            'current_release', 'blender_archive', 'blenderkit_archive',
            'blenderkit_asset_fetch', 'blenderkit_render_safe_absent',
            'capabilities_hash', 'systemd_unit', 'job_launcher',
            'agent_launcher', 'disk_state',
        }
        self.assertTrue(required.issubset(names), names)

if __name__ == '__main__':
    unittest.main()