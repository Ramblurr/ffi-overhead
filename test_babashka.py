import contextlib
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import bench

SAMPLES = [
    {"count": 1000000, "control_ms": 7, "ffi_ms": 5},
    {"count": 1000000, "control_ms": 3, "ffi_ms": 9},
]


class BabashkaHarnessTest(unittest.TestCase):
    def test_validates_adapter_output(self):
        self.assertEqual(
            SAMPLES[0], bench.validate_babashka_sample(SAMPLES[0], 1000000)
        )
        invalid = [
            None,
            [],
            1,
            {},
            {**SAMPLES[0], "count": 0},
            {**SAMPLES[0], "count": 2000000001},
            {**SAMPLES[0], "count": 2},
            {**SAMPLES[0], "ffi_ms": -1},
            {**SAMPLES[0], "control_ms": -1},
            {**SAMPLES[0], "ffi_ms": True},
            {**SAMPLES[0], "control_ms": 1.0},
            {**SAMPLES[0], "count": "1000000"},
            {**SAMPLES[0], "extra": 1},
        ]
        for sample in invalid:
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                bench.validate_babashka_sample(sample, 1000000)

    def test_subprocess_samples_and_invalid_output(self):
        for output, expected in [
            (json.dumps(SAMPLES[0]), [SAMPLES[0]] * 2),
            ("7", []),
            ("oops", []),
        ]:
            config = {"exec": [sys.executable, "-c", f"print({output!r})"]}
            samples, errors = bench.run_benchmark(config, 1000000, 2, "babashka")
            self.assertEqual(expected, samples)
            self.assertEqual(0 if expected else 2, len(errors))

    def test_invalid_pair_cannot_overwrite_existing_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            original = "Language,Average Time (ms),All Times (ms)\nbabashka,7.00,7\n"
            path.write_text(original)
            config = {"babashka": {"exec": [sys.executable, "-c", "print(7)"]}}
            argv = [
                "bench.py",
                "--update",
                "--csv",
                str(path),
                "--include",
                "babashka",
                "--count",
                "1000000",
                "--runs",
                "1",
            ]
            with patch.object(sys, "argv", argv), patch.dict(
                bench.BENCHMARKS, config, clear=True
            ), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(
                SystemExit
            ) as error:
                bench.main()
            self.assertEqual(1, error.exception.code)
            self.assertEqual(original, path.read_text())

    def test_one_selectable_entry(self):
        self.assertEqual(
            ["babashka"], [name for name, _ in bench.filter_benchmarks({"babashka"})]
        )
        self.assertNotIn("babashka/control", bench.BENCHMARKS)
        self.assertNotIn(
            "babashka", dict(bench.filter_benchmarks(exclude={"babashka"}))
        )

    def test_ffi_statistics_and_signed_difference(self):
        results = {"babashka": SAMPLES}
        self.assertEqual({"babashka": 7}, bench.calculate_averages(results))
        self.assertEqual(7, bench.calculate_stats(SAMPLES)["mean"])
        self.assertIn(
            "FFI total 7.00 ms; control 5.00 ms; incremental estimate 2.00 ms (2.000 ns/call)",
            bench.babashka_summary(results),
        )
        self.assertIn(
            "-2.00 ms (-2.000 ns/call)",
            bench.babashka_summary({"babashka": SAMPLES[:1]}),
        )
        self.assertEqual("", bench.babashka_summary({"babashka": [27335]}))

    def test_csv_round_trip_and_unrelated_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            results = {"c/static": [1, 2], "babashka": SAMPLES}
            bench.save_csv(results, bench.calculate_averages(results), path)
            self.assertEqual(results, bench.load_results_csv(path))
            with path.open() as source:
                row = list(csv.DictReader(source))[1]
            self.assertEqual(
                ["5.00", "2.00", "2.000"],
                [row[column] for column in bench.BABASHKA_CSV_COLUMNS[1:]],
            )
            merged = bench.merge_existing_results(path, {"c/static": [3, 4]})
            bench.save_csv(merged, bench.calculate_averages(merged), path)
            self.assertEqual(
                {"c/static": [3, 4], "babashka": SAMPLES}, bench.load_results_csv(path)
            )
            path.write_text(path.read_text().replace('""ffi_ms"": 5', '""ffi_ms"": 6'))
            with self.assertRaisesRegex(ValueError, "disagree"):
                bench.load_results_csv(path)

    def test_rejects_inconsistent_counts(self):
        with self.assertRaisesRegex(ValueError, "same count"):
            bench.babashka_summary(
                {"babashka": [SAMPLES[0], {**SAMPLES[1], "count": 10}]}
            )

    def test_readme_updates_table_without_babashka_commentary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "README.md"
            path.write_text(
                "Intro\n| Benchmark | Mean | Min | Max | CV | vs baseline |\n| stale |\nOutro\n"
            )
            for samples in (SAMPLES[:1], SAMPLES):
                bench.update_readme_results({"babashka": samples}, path, "babashka")
            text = path.read_text()
            self.assertNotIn("<!-- babashka-measurement -->", text)
            self.assertNotIn("incremental estimate", text)
            self.assertIn("1.00x (baseline)", text)
            self.assertIn("Outro", text)
            bench.update_readme_results({"babashka": [7]}, path, "babashka")
            self.assertNotIn("incremental estimate", path.read_text())

    def test_cli_reports_both_totals_and_saves_chart(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv = Path(tmp) / "data.csv"
            chart = Path(tmp) / "chart.png"
            config = {
                "babashka": {
                    "exec": [sys.executable, "-c", f"print({json.dumps(SAMPLES[0])!r})"]
                }
            }
            argv = [
                "bench.py",
                "--include",
                "babashka",
                "--baseline",
                "babashka",
                "--runs",
                "2",
                "--count",
                "1000000",
                "--csv",
                str(csv),
                "--chart",
                str(chart),
                "--verbose",
            ]
            output = io.StringIO()
            with patch.object(sys, "argv", argv), patch.dict(
                bench.BENCHMARKS, config, clear=True
            ), contextlib.redirect_stdout(output):
                bench.main()
            self.assertEqual(
                {"babashka": [SAMPLES[0]] * 2}, bench.load_results_csv(csv)
            )
            self.assertIn("1.00x (baseline)", output.getvalue())
            self.assertIn("control 7.00 ms", output.getvalue())
            self.assertIn("-2.000 ns/call", output.getvalue())
            self.assertTrue(chart.read_bytes().startswith(b"\x89PNG"))


class BabashkaAdapterTest(unittest.TestCase):
    def test_real_adapter(self):
        result = subprocess.run(
            ["bb", "hello.bb", "10"], capture_output=True, text=True, check=True
        )
        self.assertEqual(
            10, bench.validate_babashka_sample(json.loads(result.stdout), 10)["count"]
        )

    def test_invalid_arguments(self):
        for args in (
            [],
            ["0"],
            ["-1"],
            ["2000000001"],
            ["abc"],
            ["1.5"],
            ["1", "2"],
            ["--control", "1"],
        ):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["bb", "hello.bb", *args], capture_output=True, text=True
                )
                self.assertNotEqual(0, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertTrue(result.stderr)

    def test_each_pass_visits_every_input_in_order(self):
        # Instrument the real targets only in this small-count correctness run.
        code = """
(binding [*command-line-args* ["1"]]
  (with-out-str (load-file "hello.bb")))
(let [calls    (atom [])
      local    identity
      foreign  plusone
      record   (fn [label f]
                 (fn [x]
                   (swap! calls conj [label x (f x)])))]
  (with-redefs [identity (record "control" local)
                plusone (record "ffi" foreign)]
    (run 5))
  (println (json/generate-string @calls)))
"""
        result = subprocess.run(
            ["bb", "-e", code], capture_output=True, text=True, check=True
        )
        expected = [["control", x, x] for x in range(5)] + [
            ["ffi", x, x + 1] for x in range(5)
        ]
        self.assertEqual(expected, json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
