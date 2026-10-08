import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from record_check import check, unique_object

HERE = Path(__file__).resolve().parent


class RecordCheckTests(unittest.TestCase):
    def test_synthetic_delivery_and_input_preservation(self):
        data = json.loads((HERE / "sample.json").read_text())
        before = copy.deepcopy(data)
        expected = json.loads((HERE / "expected.json").read_text())
        self.assertEqual(check(data), expected)
        self.assertEqual(data, before)

    def test_identifier_comparison_is_exact_and_blank_ids_are_not_duplicates(self):
        data = {"required": ["id"], "records": [{"id": value} for value in ["01", "1", " 1", "1", "", " "]]}
        rows = check(data)["rows"]
        self.assertEqual([r["duplicate_of_row"] for r in rows], [None, None, None, 2, None, None])
        self.assertEqual([r["row"] for r in rows if r["missing_fields"]], [5, 6])

    def test_rejects_data_that_would_require_coercion_or_exceed_bounds(self):
        cases = [
            {"required": ["id"], "records": [{"id": 123}]},
            {"required": ["id", "id"], "records": [{"id": "a"}]},
            {"required": ["id"], "records": [{"id": "a"}] * 101},
            {"required": ["id"], "records": [{"id": "a" * 257}]},
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                check(data)

    def test_rejects_ambiguous_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"id":"first","id":"second"}', object_pairs_hook=unique_object)

    def test_cli_matches_expected_and_rejects_oversize_without_changing_file(self):
        result = subprocess.run([sys.executable, "-B", str(HERE / "record_check.py"), str(HERE / "sample.json")], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), json.loads((HERE / "expected.json").read_text()))
        with tempfile.TemporaryDirectory(dir=HERE, prefix=".test-") as folder:
            self.assertEqual(Path(folder).resolve().parent, HERE)
            path = Path(folder) / "oversize.json"
            raw = b" " * 32769
            path.write_bytes(raw)
            rejected = subprocess.run([sys.executable, "-B", str(HERE / "record_check.py"), str(path)], capture_output=True, text=True, timeout=5)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(rejected.stdout, "")
            self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
