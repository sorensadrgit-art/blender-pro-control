import sys
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))

from disk_guard import classify_free_percent


class DiskGuardTests(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(classify_free_percent(20.0), 'ok')
        self.assertEqual(classify_free_percent(14.9), 'warn')
        self.assertEqual(classify_free_percent(9.9), 'reject')
        self.assertEqual(classify_free_percent(4.9), 'emergency')

    def test_boundaries(self):
        self.assertEqual(classify_free_percent(15.0), 'ok')
        self.assertEqual(classify_free_percent(10.0), 'warn')
        self.assertEqual(classify_free_percent(5.0), 'reject')


if __name__ == '__main__':
    unittest.main()
