"""Real offline CLI regression tests. No RPC, PQC, or live settlement is exercised."""
import json
import subprocess
import unittest
from pathlib import Path

BINARY = Path(__file__).resolve().parents[1] / "target" / "debug" / "autofx-gate"
MASK = (1 << 64) - 1
MIX = 0x9E3779B97F4A7C15


def invoke(*args):
    return subprocess.run([str(BINARY), *map(str, args)], capture_output=True, text=True, timeout=10, check=False)


def reference(seed, steps):
    state = seed
    for _ in range(steps):
        rotated = ((state >> 7) | (state << 57)) & MASK
        state = (state ^ rotated ^ MIX) & MASK
    return f"{state:016x}"


class OfflineDiagnosticTests(unittest.TestCase):
    def test_zero_steps_identity(self):
        p = invoke("--seed", "0x1234", "--steps", "0")
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data, {"mode": "offline-diagnostic", "steps": 0, "state_hex": "0000000000001234"})

    def test_one_step_against_independent_reference(self):
        p = invoke("--seed", "0x1234", "--steps", "1")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["state_hex"], reference(0x1234, 1))

    def test_ten_thousand_steps_against_reference(self):
        p = invoke()
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["steps"], 10_000)
        self.assertEqual(data["state_hex"], reference(0x55AA55AA55AA55AA, 10_000))

    def test_repeated_runs_are_deterministic(self):
        self.assertEqual(invoke("--seed", "7", "--steps", "42").stdout,
                         invoke("--seed", "7", "--steps", "42").stdout)

    def test_no_unverified_production_claims(self):
        p = invoke("--steps", "1")
        self.assertEqual(p.returncode, 0)
        self.assertNotIn("100/100", p.stdout)
        self.assertNotIn("FIPS", p.stdout)
        self.assertNotIn("CONNECTED", p.stdout)


if __name__ == "__main__":
    unittest.main()
