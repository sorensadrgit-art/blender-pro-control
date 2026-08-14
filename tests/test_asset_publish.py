import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))
from asset_publish import publish_asset

class AssetPublishTests(unittest.TestCase):
    def test_publish_creates_immutable_version_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_root = root / 'work'
            published_root = root / 'published'
            source = work_root / 'props' / 'phone.blend'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'blend-bytes')
            result = publish_asset(source, 'props', 'phone', 'v001', work_root, published_root)
            self.assertTrue(Path(result['blend']).is_file())
            self.assertTrue(Path(result['metadata']).is_file())
            self.assertEqual(result['version'], 'v001')

    def test_publish_refuses_existing_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_root = root / 'work'
            published_root = root / 'published'
            source = work_root / 'props' / 'phone.blend'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'blend-bytes')
            publish_asset(source, 'props', 'phone', 'v001', work_root, published_root)
            with self.assertRaises(FileExistsError):
                publish_asset(source, 'props', 'phone', 'v001', work_root, published_root)

if __name__ == '__main__':
    unittest.main()
