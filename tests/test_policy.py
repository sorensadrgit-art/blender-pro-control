import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from pathguard import require_within

class PolicyTests(unittest.TestCase):
    def test_accepts_nested_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            target = root / "scene.blend"
            target.touch()
            self.assertEqual(require_within(target, [root]), target.resolve())

    def test_rejects_other_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            target = Path(tmp) / "other.blend"
            target.touch()
            with self.assertRaises(ValueError):
                require_within(target, [root])

if __name__ == "__main__":
    unittest.main(verbosity=2)
