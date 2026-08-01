import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from normalize_and_dedupe import comparison_key, normalize_rows  # noqa: E402


class NormalizeTests(unittest.TestCase):
    def test_comparison_key(self):
        self.assertEqual(comparison_key("  Juniper & Grain, LLC  "), "juniper and grain llc")

    def test_fictional_duplicate_is_removed(self):
        with (ROOT / "examples" / "fictional_input.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        result = normalize_rows(rows)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["dedupe_key"], "application:ex:demo1001")


if __name__ == "__main__":
    unittest.main()
