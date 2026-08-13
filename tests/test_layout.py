import unittest
from pathlib import Path

class LayoutTests(unittest.TestCase):
    def test_required_directories_exist(self):
        required = [
            "/opt/blender-pro",
            "/srv/blender-pro",
            "/var/cache/blender-pro",
            "/var/log/blender-pro",
        ]
        for raw in required:
            self.assertTrue(Path(raw).is_dir(), raw)

if __name__ == "__main__":
    unittest.main(verbosity=2)
