import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import bench


class MergeExistingResultsTest(unittest.TestCase):
    def test_preserves_unselected_results_and_replaces_selected_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            csv_path.write_text(
                "Language,Average Time (ms),All Times (ms)\n"
                'alpha,2.00,"1,3"\n'
                'beta,5.00,"4,6"\n'
            )

            merged = bench.merge_existing_results(csv_path, {"beta": [7, 9]})

            self.assertEqual({"alpha": [1, 3], "beta": [7, 9]}, merged)

    def test_rejects_csv_with_unexpected_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            csv_path.write_text("Language,Average Time (ms)\nalpha,2.00\n")

            with self.assertRaisesRegex(ValueError, "header"):
                bench.merge_existing_results(csv_path, {"beta": [7, 9]})


class UpdateCliTest(unittest.TestCase):
    def test_update_requires_csv_path(self):
        result = subprocess.run(
            [sys.executable, "bench.py", "--update"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("--update requires --csv", result.stderr)

    def test_update_requires_existing_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_csv = Path(tmpdir) / "missing.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    "bench.py",
                    "--update",
                    "--csv",
                    str(missing_csv),
                    "--include",
                    "c/static",
                    "--count",
                    "1",
                ],
                capture_output=True,
                text=True,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("--update CSV does not exist", result.stderr)

    def test_update_cli_preserves_existing_benchmark_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            readme_path = Path(tmpdir) / "README.md"
            csv_path.write_text(
                "Language,Average Time (ms),All Times (ms)\n" 'alpha,2.00,"1,3"\n'
            )
            readme_path.write_text(
                "Intro\n"
                "| Benchmark | Mean | Min | Max | Std dev | vs baseline |\n"
                "|---|---:|---:|---:|---:|---:|\n"
                "| stale | 0 ms | 0 ms | 0 ms | 0.0 ms | stale |\n"
                "Outro\n"
            )
            argv = [
                "bench.py",
                "--update",
                "--csv",
                str(csv_path),
                "--include",
                "test",
                "--baseline",
                "alpha",
                "--readme",
                str(readme_path),
                "--runs",
                "1",
                "--count",
                "1",
            ]
            benchmark = {"test": {"exec": [sys.executable, "-c", "print(7)"]}}

            with patch.object(sys, "argv", argv), patch.dict(
                bench.BENCHMARKS, benchmark, clear=True
            ):
                bench.main()

            self.assertEqual(
                {"alpha": [1, 3], "test": [7]}, bench.load_results_csv(csv_path)
            )
            self.assertEqual(
                "Intro\n"
                "| Benchmark | Mean | Min | Max | CV | vs baseline |\n"
                "|---|---:|---:|---:|---:|---:|\n"
                "| alpha | 2 ms | 1 ms | 3 ms | 70.7% | 1.00x (baseline) |\n"
                "| test | 7 ms | 7 ms | 7 ms | 0.0% | 3.50x slower |\n"
                "Outro\n",
                readme_path.read_text(),
            )


if __name__ == "__main__":
    unittest.main()
