#!/usr/bin/env python3

import argparse
import subprocess
import csv
import statistics
import sys
from pathlib import Path

BENCHMARKS = [
    ("luajit", ["luajit", "hello.lua"]),
    ("c", ["./c_hello"]),
    ("cpp", ["./cpp_hello"]),
    ("Common Lisp via SBCL", ["sbcl", "--script", "hello.lisp"]),
    ("zig", ["./zig-out/zig_hello/zig_hello"]),
    ("v", ["./v_hello"]),
    ("rust", ["./rust_hello"]),
    ("d", ["./d_hello"]),
    ("d ldc2", ["./d_ldc2_hello"]),
    ("haskell", ["./ghc_hello"]),
    ("ocamlopt", ["./ocaml/test.nat"]),
    ("ocamlc", ["./ocaml/test.bc"]),
    ("csharp mono", ["mono", "./csharp_hello.exe"]),
    ("java8", ["./vendor/openjdk8/bin/java", "-cp", ".", "jhello.Hello"]),
    (
        "java21",
        [
            "./vendor/openjdk21/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello21",
            "jhello.Hello",
        ],
    ),
    (
        "java24",
        [
            "./vendor/openjdk24/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello24",
            "jhello.Hello",
        ],
    ),
    (
        "java21 panama",
        [
            "./vendor/openjdk21/bin/java",
            "--enable-preview",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            ".",
            "jhello_panama.Hello",
        ],
    ),
    (
        "java24 panama",
        [
            "./vendor/openjdk24/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello_panama24",
            "jhello_panama.Hello",
        ],
    ),
    ("node", ["node", "hello.js"]),
    ("go", ["./go_hello"]),
    ("elixir", ["elixir", "-r", "hello.ex", "-e", "S.start"]),
    ("julia", ["julia", "hello.jl"]),
]


def run_benchmark(cmd, count, runs=2):
    times = []
    for _ in range(runs):
        try:
            result = subprocess.run(
                cmd + [str(count)], capture_output=True, text=True, check=True
            )
            time = int(result.stdout.strip())
            if time > 0:
                times.append(time)
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
            continue
    return times


def run_all_benchmarks(count, runs):
    results = {}
    for name, cmd in BENCHMARKS:
        times = run_benchmark(cmd, count, runs)
        if times:
            results[name] = times
    return results


def calculate_averages(results):
    return {lang: statistics.mean(times) for lang, times in results.items()}


def save_csv(results, averages, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Language", "Average Time (ms)", "All Times (ms)"])
        for lang in sorted(averages.keys(), key=lambda x: averages[x]):
            times_str = ",".join(str(t) for t in results[lang])
            writer.writerow([lang, f"{averages[lang]:.2f}", times_str])


def create_chart(averages, filename):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    sorted_items = sorted(averages.items(), key=lambda x: x[1])
    languages, times = zip(*sorted_items)

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(range(len(languages)), times, color="steelblue", alpha=0.7)

    ax.set_xlabel("Programming Languages")
    ax.set_ylabel("Average Time (milliseconds)")
    ax.set_title("FFI Overhead Benchmark Results")
    ax.set_xticks(range(len(languages)))
    ax.set_xticklabels(languages, rotation=45, ha="right")

    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + max(times) * 0.01,
            f"{time:.0f}ms",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="FFI Overhead Benchmarking Harness")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--count", type=int, default=500000000)
    parser.add_argument("--csv", default="benchmark_results.csv")
    parser.add_argument("--chart", default="benchmark_chart.png")

    args = parser.parse_args()

    results = run_all_benchmarks(args.count, args.runs)
    if not results:
        sys.exit(1)

    averages = calculate_averages(results)
    save_csv(results, averages, args.csv)

    for i, (lang, avg_time) in enumerate(
        sorted(averages.items(), key=lambda x: x[1]), 1
    ):
        print(f"{i:2}. {lang:<25} {avg_time:8.2f} ms")

    create_chart(averages, args.chart)


if __name__ == "__main__":
    main()
