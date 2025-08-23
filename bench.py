#!/usr/bin/env python3

import argparse
import subprocess
import csv
import statistics
import sys
from pathlib import Path

BENCHMARKS = {
    "luajit": {"exec": ["luajit", "hello.lua"]},
    "c": {"exec": ["./c_hello"]},
    "cpp": {"exec": ["./cpp_hello"]},
    "CL/SBCL": {"exec": ["sbcl", "--script", "hello.lisp"]},
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
    "java24/jni": {
        "exec": [
            "./vendor/openjdk24/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello24",
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
    "java24/panama": {
        "exec": [
            "./vendor/openjdk24/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            "jhello_panama24",
            "jhello_panama.Hello",
        ]
    },
    "node": {"exec": ["node", "hello.js"]},
    "go": {"exec": ["./go_hello"]},
    "elixir": {"exec": ["elixir", "-r", "hello.ex", "-e", "S.start"]},
    "julia": {"exec": ["julia", "hello.jl"]},
    "janet": {"exec": ["janet", "hello.janet"]},
    # this is measuring jvm startup time too, so it's not very fair
    # "clojure/coffi": {
    #    "cwd": "clojure_coffi",
    #    "exec": ["clj", "-J--enable-native-access=ALL-UNNAMED", "-M", "hello.clj"],
    # },
}


def run_benchmark(benchmark_config, count, runs=2, name=""):
    times = []
    cwd = benchmark_config.get("cwd")
    cmd = benchmark_config["exec"]

    for _ in range(runs):
        try:
            result = subprocess.run(
                cmd + [str(count)], capture_output=True, text=True, check=True, cwd=cwd
            )
            time = int(result.stdout.strip())
            times.append(time)
        except subprocess.CalledProcessError as e:
            print(f"ERROR {name}: Command failed with exit code {e.returncode}")
            print(f"  Command: {' '.join(cmd)}")
            print(f"  stderr: {e.stderr.strip()}")
            continue
        except ValueError as e:
            print(f"ERROR {name}: Invalid output - {e}")
            print(f"  stdout: {result.stdout.strip()}")
            continue
        except FileNotFoundError:
            print(f"ERROR {name}: Command not found - {cmd[0]}")
            continue
    return times


def run_all_benchmarks(count, runs, include=None, exclude=None):
    results = {}
    for name, benchmark_config in BENCHMARKS.items():
        if include and name not in include:
            continue
        if exclude and name in exclude:
            continue
        times = run_benchmark(benchmark_config, count, runs, name)
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
    ax.set_title("FFI Overhead Benchmark Results (Lower is Better)")
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
    parser.add_argument("--csv", default=None)
    parser.add_argument("--chart", default=None)
    parser.add_argument(
        "--include", help="Comma-separated list of languages to include"
    )
    parser.add_argument(
        "--exclude", help="Comma-separated list of languages to exclude"
    )

    args = parser.parse_args()

    include = set(args.include.split(",")) if args.include else None
    exclude = set(args.exclude.split(",")) if args.exclude else None

    results = run_all_benchmarks(args.count, args.runs, include, exclude)
    if not results:
        sys.exit(1)

    averages = calculate_averages(results)
    if args.csv:
        save_csv(results, averages, args.csv)

    for i, (lang, avg_time) in enumerate(
        sorted(averages.items(), key=lambda x: x[1]), 1
    ):
        print(f"{i:2}. {lang:<25} {avg_time:8.2f} ms")

    if args.chart:
        create_chart(averages, args.chart)


if __name__ == "__main__":
    main()
