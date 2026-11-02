"""Static integrity checks for the standalone GitHub Pages experiment.

These tests do not substitute for Chromium interaction tests or validate the
shore's physical assumptions. They detect missing controls, external assets,
and accidental breakage of the embedded JavaScript syntax.
"""
import html.parser
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"


class _Elements(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.remote_scripts = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "script" and "src" in d:
            self.remote_scripts.append(d["src"])


class PagesLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = HTML.read_text(encoding="utf-8")
        cls.parsed = _Elements()
        cls.parsed.feed(cls.page)

    def test_controls_are_present(self):
        expected = {
            "shore", "spectrum", "readchart", "long", "mid", "short",
            "orchestra", "read", "reset", "feedback", "driveSource",
            "force", "thresh", "order", "orderx", "export", "compareResult",
        }
        self.assertFalse(expected - self.parsed.ids)

    def test_self_contained_no_remote_js(self):
        self.assertEqual(self.parsed.remote_scripts, [])
        self.assertNotIn("fetch(", self.page)
        self.assertNotIn("import(", self.page)

    def test_conserved_flux_and_control_are_not_omitted(self):
        for required in (
            "m.flux[j]", "h[j]-=move;h[j+1]+=move",
            "if(!bounded)", "source==='resonant'",
            "source==='edge'?", "Fixed wave + bounded sand",
            "Fixed wave + unbounded additive sand",
            "energy", "powerSpectrum", "readSingle",
        ):
            self.assertIn(required, self.page)

    def test_inline_javascript_parses_if_node_is_available(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable")
        scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", self.page, re.S)
        self.assertEqual(len(scripts), 1)
        result = subprocess.run(
            [node, "--check", "-"],
            input=scripts[0], text=True, capture_output=True,
            timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
