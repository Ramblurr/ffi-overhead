#!/usr/bin/env python3

import argparse
import subprocess
import csv
import statistics
import sys
import math
import os
from pathlib import Path

BENCHMARKS = {
    "luajit": {"exec": ["luajit", "hello.lua"]},
    "c/dynamic": {"exec": ["./c_hello"]},
    "c/static": {"exec": ["./c_static_hello"]},
    "cpp": {"exec": ["./cpp_hello"]},
    "CL/SBCL": {"exec": ["sbcl", "--script", "hello.lisp"]},
    "chez": {
        "exec": [
            "scheme",
            "--quiet",
            "--optimize-level",
            "3",
            "--script",
            "hello.ss",
        ]
    },
    "zig": {"exec": ["./zig-out/zig_hello/zig_hello"]},
    "v": {"exec": ["./v_hello"]},
    "rust": {"exec": ["./rust_hello"]},
    "d": {"exec": ["./d_hello"]},
    "d ldc2": {"exec": ["./d_ldc2_hello"]},
    "haskell": {"exec": ["./ghc_hello"]},
    "ocamlopt": {"exec": ["./ocaml/test.nat"]},
    "ocamlc": {"exec": ["./ocaml/test.bc"]},
    "csharp mono": {"exec": ["mono", "./csharp_hello.exe"]},
    "java8/jni": {"exec": ["./vendor/openjdk8/bin/java", "-cp", ".", "jhello.Hello"]},
    "java21/jni": {
        "exec": [
            "./vendor/openjdk21/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello21",
            "jhello.Hello",
        ]
    },
    "java25/jni": {
        "exec": [
            "./vendor/openjdk25/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello25",
            "jhello.Hello",
        ]
    },
    "java21/panama": {
        "exec": [
            "./vendor/openjdk21/bin/java",
            "--enable-preview",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            ".",
            "jhello_panama.Hello",
        ]
    },
    "java25/panama": {
        "exec": [
            "./vendor/openjdk25/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello_panama25",
            "jhello_panama.Hello",
        ]
    },
    "node": {"exec": ["node", "hello.js"]},
    "go": {"exec": ["./go_hello"]},
    "elixir": {"exec": ["elixir", "-r", "hello.ex", "-e", "S.start"]},
    "julia": {"exec": ["julia", "hello.jl"]},
    "janet": {"exec": ["janet", "hello.janet"]},
    "jolt": {"exec": ["./jolt_hello"]},
    "babashka": {"exec": ["bb", "hello.bb"]},
    "clj/panama": {
        "cwd": "clojure_panama",
        "exec": [
            "clojure",
            "-J--enable-native-access=ALL-UNNAMED",
            "-Sdeps",
            '{:paths ["hello.jar"]}',
            "-M",
            "-m",
            "clojure-panama.hello",
        ],
    },
    "clj/coffi": {
        "cwd": "clojure_coffi",
        "exec": [
            "clj",
            "-J--enable-native-access=ALL-UNNAMED",
            "-Sdeps",
            '{:paths ["hello.jar"]}',
            "-M",
            "-m",
            "ffi-overhead.coffi",
        ],
        "tty_detach": True,
    },
}


def calculate_stats(times):
    """Calculate statistical measures for a list of times."""
    if not times:
        return {"mean": 0, "min": 0, "max": 0, "stddev": 0}

    mean_val = statistics.mean(times)
    min_val = min(times)
    max_val = max(times)
    stddev_val = statistics.stdev(times) if len(times) > 1 else 0

    return {"mean": mean_val, "min": min_val, "max": max_val, "stddev": stddev_val}


def format_comparison(mean_time, baseline_time, is_baseline=False):
    """Format comparison string against baseline."""
    if baseline_time is None:
        return "N/A"

    # If this is the actual baseline benchmark
    if is_baseline:
        return "1.00x (baseline)"

    # Handle zero or near-zero times
    if baseline_time <= 0.001:  # Less than 1 microsecond
        if mean_time <= 0.001:
            return "~equal (both ~0ms)"
        else:
            return "N/A (baseline ~0ms)"

    if mean_time <= 0.001:  # Less than 1 microsecond
        return "N/A (mean ~0ms)"

    if abs(mean_time - baseline_time) < 0.01:  # Consider very close times as equal
        return "~equal"

    ratio = mean_time / baseline_time
    if ratio > 1:
        return f"{ratio:.2f}x slower"
    else:
        return f"{1/ratio:.2f}x faster"


def calculate_column_widths(results_dict, stats_dict, has_comparison):
    """Calculate optimal column widths based on data."""
    widths = {
        "benchmark": max(
            10, max(len(name) for name in results_dict.keys()) if results_dict else 10
        ),
        "mean": 8,
        "min": 8,
        "max": 8,
        "stddev": 8,
    }

    if has_comparison:
        widths["comparison"] = 20

    # Adjust timing columns based on actual values
    if stats_dict:
        max_mean = max(stats["mean"] for stats in stats_dict.values())
        max_min = max(stats["min"] for stats in stats_dict.values())
        max_max = max(stats["max"] for stats in stats_dict.values())
        max_stddev = max(stats["stddev"] for stats in stats_dict.values())

        widths["mean"] = max(8, len(f"{max_mean:.0f} ms"))
        widths["min"] = max(8, len(f"{max_min:.0f} ms"))
        widths["max"] = max(8, len(f"{max_max:.0f} ms"))
        widths["stddev"] = max(8, len(f"{max_stddev:.1f} ms"))

    return widths


def format_table_row(columns, widths, alignments):
    """Format a table row with proper alignment."""
    formatted_cols = []
    for i, (col, width, align) in enumerate(zip(columns, widths, alignments)):
        if align == "left":
            formatted_cols.append(f"{col:<{width}}")
        else:  # right
            formatted_cols.append(f"{col:>{width}}")

    return "│ " + " │ ".join(formatted_cols) + " │"


def print_table_header(runs, count, widths, has_comparison):
    """Print the table header with configuration info."""
    print(f"\nBenchmark Results ({runs} runs, count={count:,})")

    # Calculate total width for separator
    total_width = (
        sum(widths.values()) + len(widths) * 3 + 1
    )  # 3 chars per column separator + 1 for final │
    print("─" * total_width)

    # Header row
    headers = ["Benchmark", "Mean", "Min", "Max", "Std Dev"]
    header_widths = [
        widths["benchmark"],
        widths["mean"],
        widths["min"],
        widths["max"],
        widths["stddev"],
    ]
    alignments = ["left", "right", "right", "right", "right"]

    if has_comparison:
        headers.append("vs Baseline")
        header_widths.append(widths["comparison"])
        alignments.append("right")

    print(format_table_row(headers, header_widths, alignments))
    print("─" * total_width)


def print_benchmark_result(name, stats, widths, has_comparison, baseline_time=None):
    """Print a single benchmark result row."""
    columns = [
        name,
        f"{stats['mean']:.0f} ms",
        f"{stats['min']:.0f} ms",
        f"{stats['max']:.0f} ms",
        f"{stats['stddev']:.1f} ms",
    ]

    column_widths = [
        widths["benchmark"],
        widths["mean"],
        widths["min"],
        widths["max"],
        widths["stddev"],
    ]
    alignments = ["left", "right", "right", "right", "right"]

    if has_comparison and baseline_time is not None:
        columns.append(format_comparison(stats["mean"], baseline_time))
        column_widths.append(widths["comparison"])
        alignments.append("right")

    print(format_table_row(columns, column_widths, alignments))


def run_benchmark(benchmark_config, count, runs=2, name=""):
    times = []
    errors = []
    cwd = benchmark_config.get("cwd")
    cmd = benchmark_config["exec"]
    tty_detach = benchmark_config.get("tty_detach", False)

    for _ in range(runs):
        try:
            # Check if we need to detach from terminal to prevent TTY output
            if tty_detach:
                result = subprocess.run(
                    cmd + [str(count)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    check=True,
                    cwd=cwd,
                    start_new_session=True,  # Detach from terminal session
                )
            else:
                result = subprocess.run(
                    cmd + [str(count)],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=cwd,
                )
            # Strip all whitespace including newlines
            output = result.stdout.strip()
            time = int(output)
            times.append(time)
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}"
            errors.append(error_msg)
            continue
        except ValueError as e:
            error_msg = f"Invalid output - expected integer"
            errors.append(error_msg)
            continue
        except FileNotFoundError:
            error_msg = f"Command not found - {cmd[0]}"
            errors.append(error_msg)
            continue

    return times, errors


def filter_benchmarks(include=None, exclude=None):
    """Filter benchmarks based on include/exclude criteria."""
    benchmarks_to_run = []
    for name, benchmark_config in BENCHMARKS.items():
        if include and name not in include:
            continue
        if exclude and name in exclude:
            continue
        benchmarks_to_run.append((name, benchmark_config))
    return benchmarks_to_run


def setup_table_display(benchmarks_to_run, runs, count, baseline):
    """Setup table display and return column widths."""
    # Calculate optimal widths based on all benchmark names and estimated values
    temp_results = {name: [0] for name, _ in benchmarks_to_run}
    # Use maximum expected values for width calculation
    temp_stats = {
        name: {"mean": 99999, "min": 99999, "max": 99999, "stddev": 999.9}
        for name, _ in benchmarks_to_run
    }
    widths = calculate_column_widths(temp_results, temp_stats, baseline is not None)
    print_table_header(runs, count, widths, baseline is not None)
    return widths


def update_baseline_time(baseline, baseline_time, name, stats):
    """Update baseline time based on baseline strategy."""
    if baseline:
        if baseline == "first" and baseline_time is None:
            return stats[name]["mean"]
        elif baseline == name:
            return stats[name]["mean"]
    return baseline_time


def print_success_row(name, stats, widths, baseline, baseline_time):
    """Print a successful benchmark result row."""
    columns = [
        name,
        f"{stats['mean']:.0f} ms",
        f"{stats['min']:.0f} ms",
        f"{stats['max']:.0f} ms",
        f"{stats['stddev']:.1f} ms",
    ]

    column_widths = [
        widths["benchmark"],
        widths["mean"],
        widths["min"],
        widths["max"],
        widths["stddev"],
    ]
    alignments = ["left", "right", "right", "right", "right"]

    if baseline is not None:
        is_baseline = name == baseline
        comparison = format_comparison(stats["mean"], baseline_time, is_baseline)
        columns.append(comparison)
        column_widths.append(widths["comparison"])
        alignments.append("right")

    print(format_table_row(columns, column_widths, alignments))


def print_error_row(name, widths, baseline):
    """Print an error benchmark result row."""
    columns = [name, "ERROR", "ERROR", "ERROR", "ERROR"]
    column_widths = [
        widths["benchmark"],
        widths["mean"],
        widths["min"],
        widths["max"],
        widths["stddev"],
    ]
    alignments = ["left", "right", "right", "right", "right"]

    if baseline is not None:
        columns.append("ERROR")
        column_widths.append(widths["comparison"])
        alignments.append("right")

    print(format_table_row(columns, column_widths, alignments))


def clear_running_indicator():
    """Clear the entire running indicator line."""
    # Try ANSI escape code first, fallback to spaces if needed
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        # Move to beginning of line and clear to end of line
        print("\r\033[K", end="")
    else:
        # Fallback: overwrite entire line with spaces (assuming max 120 chars)
        print(f"\r{' ' * 120}\r", end="")


def print_final_separator(widths):
    """Print the final table separator."""
    total_width = sum(widths.values()) + len(widths) * 3 + 1
    print("─" * total_width)


def print_errors_summary(all_errors):
    """Print summary of all errors encountered."""
    if all_errors:
        print("\nErrors:")
        for name, errors in all_errors.items():
            print(f"  {name}:")
            for error in errors:
                print(f"    - {error}")


def run_all_benchmarks(
    count, runs, include=None, exclude=None, verbose=False, baseline=None
):
    results = {}
    stats = {}
    all_errors = {}
    baseline_time = None

    # Filter benchmarks to run
    benchmarks_to_run = filter_benchmarks(include, exclude)

    # If baseline is specified, ensure it runs first
    if baseline and baseline != "first":
        # Find the baseline benchmark and move it to the front
        baseline_benchmark = None
        remaining_benchmarks = []

        for name, config in benchmarks_to_run:
            if name == baseline:
                baseline_benchmark = (name, config)
            else:
                remaining_benchmarks.append((name, config))

        if baseline_benchmark:
            benchmarks_to_run = [baseline_benchmark] + remaining_benchmarks

    # Setup table display if verbose
    widths = None
    if verbose:
        widths = setup_table_display(benchmarks_to_run, runs, count, baseline)

    # Run each benchmark
    for name, benchmark_config in benchmarks_to_run:
        if verbose and widths:
            # Show running indicator in table format with "..." in timing columns
            running_cols = [name, "...", "", "", ""]
            running_widths = [
                widths["benchmark"],
                widths["mean"],
                widths["min"],
                widths["max"],
                widths["stddev"],
            ]
            running_alignments = ["left", "left", "left", "left", "left"]
            if baseline is not None:
                running_cols.append("")
                running_widths.append(widths["comparison"])
                running_alignments.append("left")
            print(
                format_table_row(running_cols, running_widths, running_alignments),
                end="",
                flush=True,
            )

        times, errors = run_benchmark(benchmark_config, count, runs, name)

        if verbose:
            clear_running_indicator()

        if errors:
            all_errors[name] = errors

        if times:
            # Process successful benchmark
            results[name] = times
            stats[name] = calculate_stats(times)
            baseline_time = update_baseline_time(baseline, baseline_time, name, stats)

            if verbose and widths:
                print_success_row(name, stats[name], widths, baseline, baseline_time)
        else:
            # Process failed benchmark
            if verbose and widths:
                print_error_row(name, widths, baseline)

    # Finish table display
    if verbose and (results or all_errors):
        if not widths:  # In case no benchmarks ran
            widths = calculate_column_widths({}, {}, baseline is not None)
        print_final_separator(widths)

    # Print error summary
    print_errors_summary(all_errors)

    return results, all_errors


def calculate_averages(results):
    return {lang: statistics.mean(times) for lang, times in results.items()}


def load_results_csv(filename):
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        expected_header = ["Language", "Average Time (ms)", "All Times (ms)"]
        if reader.fieldnames != expected_header:
            raise ValueError(
                f"unexpected CSV header: expected {','.join(expected_header)}"
            )
        return {
            row["Language"]: [int(value) for value in row["All Times (ms)"].split(",")]
            for row in reader
        }


def merge_existing_results(filename, new_results):
    results = load_results_csv(filename)
    results.update(new_results)
    return results


def save_csv(results, averages, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["Language", "Average Time (ms)", "All Times (ms)"])
        for lang in sorted(averages.keys(), key=lambda x: averages[x]):
            times_str = ",".join(str(t) for t in results[lang])
            writer.writerow([lang, f"{averages[lang]:.2f}", times_str])


def save_toolchain_report(filename):
    project_dir = Path(__file__).resolve().parent
    result = subprocess.run(
        [project_dir / "check-environment.sh"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    Path(filename).write_text(result.stdout)


def create_chart(averages, filename, count, runs):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    sorted_items = sorted(averages.items(), key=lambda item: item[1])
    languages, times = zip(*sorted_items)
    positions = range(len(languages))

    fig, ax = plt.subplots(figsize=(10, max(5, len(languages) * 0.25 + 1.5)))
    ax.scatter(times, positions, color="steelblue", s=32, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(min(times) / 1.25, max(times) * 1.5)
    ax.set_xlabel(f"Total elapsed time for {count:,} FFI calls (ms, logarithmic scale)")
    ax.set_title(
        "FFI Overhead Benchmark Results — Lower is Better\n"
        f"Mean across {runs} runs; values are total benchmark time, not latency per call"
    )
    ax.set_yticks(positions, labels=languages)
    ax.invert_yaxis()
    ax.grid(axis="x", which="both", linestyle=":", linewidth=0.7, alpha=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)

    for position, time in zip(positions, times):
        ax.annotate(
            f"{time:.0f} ms",
            (time, position),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.2},
        )

    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return True


def main():
    parser = argparse.ArgumentParser(description="FFI Overhead Benchmarking Harness")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--count", type=int, default=500000000)
    parser.add_argument("--csv", default=None)
    parser.add_argument("--chart", default=None)
    parser.add_argument(
        "--toolchain",
        help="Write toolchain versions and build provenance to this file",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Merge selected benchmark results into an existing --csv dataset",
    )
    parser.add_argument(
        "--include", help="Comma-separated list of languages to include"
    )
    parser.add_argument(
        "--exclude", help="Comma-separated list of languages to exclude"
    )
    parser.add_argument(
        "--baseline", help="Benchmark to use as baseline for comparison"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Display results in table format"
    )

    args = parser.parse_args()
    if args.update and not args.csv:
        parser.error("--update requires --csv")
    if args.update and not Path(args.csv).is_file():
        parser.error(f"--update CSV does not exist: {args.csv}")

    include = set(args.include.split(",")) if args.include else None
    exclude = set(args.exclude.split(",")) if args.exclude else None

    known_benchmarks = set(BENCHMARKS)
    for option, requested in (("--include", include), ("--exclude", exclude)):
        unknown = requested - known_benchmarks if requested else set()
        if unknown:
            parser.error(
                f"{option} contains unknown benchmark(s): {', '.join(sorted(unknown))}"
            )

    selected_benchmarks = filter_benchmarks(include, exclude)
    selected_names = {name for name, _ in selected_benchmarks}
    if (
        args.baseline
        and args.baseline != "first"
        and args.baseline not in selected_names
    ):
        parser.error(f"--baseline benchmark is not selected: {args.baseline}")
    results, errors = run_all_benchmarks(
        args.count, args.runs, include, exclude, args.verbose, args.baseline
    )
    complete = set(results) == selected_names and all(
        len(times) == args.runs for times in results.values()
    )
    if errors or not results or not complete:
        sys.exit(1)

    if args.update:
        results = merge_existing_results(args.csv, results)

    averages = calculate_averages(results)
    if args.csv:
        save_csv(results, averages, args.csv)

    # Only print simple list format if not in verbose mode
    if not args.verbose:
        for i, (lang, avg_time) in enumerate(
            sorted(averages.items(), key=lambda x: x[1]), 1
        ):
            print(f"{i:2}. {lang:<25} {avg_time:8.2f} ms")

    if args.chart:
        create_chart(averages, args.chart, args.count, args.runs)

    if args.toolchain:
        save_toolchain_report(args.toolchain)


if __name__ == "__main__":
    main()
