import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path('/root/blender-pro-control/.worktrees/build-vps-foundation/runtime')
sys.path.insert(0, str(RUNTIME))
from manifest import validate_manifest

class ManifestTests(unittest.TestCase):
    def valid(self, root):
        scene = root / 'projects' / 'shot.blend'
        scene.parent.mkdir(parents=True)
        scene.write_bytes(b'x')
        return {
            'schema': 1,
            'project': 'smoke',
            'scene': str(scene),
            'engine': 'CYCLES',
            'frame': 1,
            'resolution': [320, 180],
            'preview_output': str(root / 'previews' / 'smoke.png'),
            'render_output': str(root / 'renders' / 'smoke.png'),
        }

    def test_valid_manifest_is_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_manifest(self.valid(root), root / 'projects', root / 'assets', root / 'previews', root / 'renders')
            self.assertEqual(result['engine'], 'CYCLES')
            self.assertEqual(result['frame'], 1)

    def test_arbitrary_command_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.valid(root)
            data['command'] = 'bash anything'
            with self.assertRaises(ValueError):
                validate_manifest(data, root / 'projects', root / 'assets', root / 'previews', root / 'renders')

if __name__ == '__main__':
    unittest.main()
