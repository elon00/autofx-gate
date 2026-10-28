"""Negative controls for the bounded offline diagnostic CLI."""
import subprocess
import unittest
from pathlib import Path

BINARY = Path(__file__).resolve().parents[1] / "target" / "debug" / "autofx-gate"


def invoke(*args):
    return subprocess.run([str(BINARY), *args], capture_output=True, text=True, timeout=10, check=False)


class FailClosedTests(unittest.TestCase):
    def assert_rejected(self, *args):
        p = invoke(*args)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(p.stdout, "")
        self.assertIn("offline diagnostic error", p.stderr)

    def test_reject_negative_steps(self):
        self.assert_rejected("--steps", "-1")

    def test_reject_excessive_steps(self):
        self.assert_rejected("--steps", "100001")

    def test_reject_integer_overflow(self):
        self.assert_rejected("--seed", "0x10000000000000000")

    def test_reject_unknown_flag(self):
        self.assert_rejected("--rpc", "https://example.invalid")

    def test_reject_missing_value(self):
        self.assert_rejected("--seed")

    def test_reject_duplicate_flag(self):
        self.assert_rejected("--steps", "1", "--steps", "2")


if __name__ == "__main__":
    unittest.main()
