import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

import render_start_main


class RenderStartMainTests(unittest.TestCase):
    def test_rejects_wrong_argument_count(self):
        called = []
        code = render_start_main.main([], run=lambda *a, **k: called.append((a, k)))
        self.assertEqual(code, 64)
        self.assertEqual(called, [])

    def test_rejects_unsafe_instance_slug(self):
        called = []
        code = render_start_main.main(['../../root'], run=lambda *a, **k: called.append((a, k)))
        self.assertEqual(code, 65)
        self.assertEqual(called, [])

    def test_starts_exact_systemd_unit_without_shell(self):
        calls = []

        def fake_run(argv, **kwargs):
            calls.append((argv, kwargs))
            return SimpleNamespace(returncode=7)

        code = render_start_main.main(['smoke-job'], run=fake_run)
        self.assertEqual(code, 7)
        self.assertEqual(calls, [([
            '/usr/bin/systemctl',
            'start',
            'blender-pro-render@smoke-job.service',
        ], {'check': False, 'shell': False})])


if __name__ == '__main__':
    unittest.main()
