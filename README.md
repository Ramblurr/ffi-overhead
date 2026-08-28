ffi-overhead
============

comparing the c ffi overhead on various programming languages

# Results (2026-08)

> [!WARNING]
> I have no idea what I am doing. Do not believe this.

![FFI Overhead Benchmark Results for 2026-08](data/2026-08/chart.png)

*Chart shows average execution times across 10 runs on a logarithmic scale. Lower values are better.*

*CV is sample standard deviation divided by mean. Absolute timings remain in the raw CSV.*

| Benchmark | Mean | Min | Max | CV | vs baseline |
|---|---:|---:|---:|---:|---:|
| c/static | 890 ms | 841 ms | 1146 ms | 10.4% | 1.00x (baseline) |
| zig | 861 ms | 844 ms | 911 ms | 2.4% | 1.03x faster |
| julia | 874 ms | 847 ms | 902 ms | 2.2% | 1.02x faster |
| rust | 1343 ms | 1333 ms | 1373 ms | 0.8% | 1.51x slower |
| v | 1358 ms | 1341 ms | 1377 ms | 0.7% | 1.53x slower |
| d | 1532 ms | 1509 ms | 1576 ms | 1.4% | 1.72x slower |
| c/dynamic | 1534 ms | 1517 ms | 1568 ms | 1.1% | 1.72x slower |
| d ldc2 | 1539 ms | 1510 ms | 1562 ms | 1.1% | 1.73x slower |
| haskell | 1557 ms | 1506 ms | 1632 ms | 2.7% | 1.75x slower |
| cpp | 1572 ms | 1521 ms | 1692 ms | 3.1% | 1.76x slower |
| ocamlopt | 1714 ms | 1691 ms | 1753 ms | 1.2% | 1.92x slower |
| CL/SBCL | 2034 ms | 1986 ms | 2128 ms | 2.1% | 2.28x slower |
| java21/panama | 2265 ms | 2188 ms | 2316 ms | 1.6% | 2.54x slower |
| chez | 2325 ms | 2257 ms | 2410 ms | 2.0% | 2.61x slower |
| java25/panama | 2447 ms | 2344 ms | 2904 ms | 6.7% | 2.75x slower |
| luajit | 2457 ms | 2442 ms | 2482 ms | 0.5% | 2.76x slower |
| java25/jni | 3091 ms | 3043 ms | 3150 ms | 1.1% | 3.47x slower |
| java8/jni | 3104 ms | 3038 ms | 3292 ms | 2.5% | 3.49x slower |
| java21/jni | 3298 ms | 3218 ms | 3394 ms | 1.8% | 3.70x slower |
| clj/panama | 4454 ms | 4350 ms | 4729 ms | 3.3% | 5.00x slower |
| ocamlc | 4505 ms | 4338 ms | 4863 ms | 3.6% | 5.06x slower |
| clj/coffi | 5111 ms | 4926 ms | 5504 ms | 3.9% | 5.74x slower |
| jolt | 5571 ms | 5209 ms | 5928 ms | 4.2% | 6.26x slower |
| node | 6776 ms | 6664 ms | 6942 ms | 1.2% | 7.61x slower |
| elixir | 16662 ms | 16307 ms | 17405 ms | 2.1% | 18.71x slower |
| go | 17389 ms | 17169 ms | 17662 ms | 1.0% | 19.53x slower |
| csharp mono | 35991 ms | 35685 ms | 36296 ms | 0.7% | 40.42x slower |
| janet | 48456 ms | 47429 ms | 49488 ms | 1.3% | 54.41x slower |
| babashka | 64068 ms | 63115 ms | 65191 ms | 1.1% | 71.95x slower |

Ran on an AMD EPYC CPU.

Raw data: [data/2026-08/data.csv](./data/2026-08/data.csv)

Toolchain versions and build provenance: [data/2026-08/toolchain.txt](./data/2026-08/toolchain.txt)

Previous results: [2025-08 data](./data/2025-08/data.csv), [chart](./data/2025-08/chart.png), and [toolchain](./data/2025-08/toolchain.txt).

Each implementation calls this native function `count` times:

```c
int plusone(int x)
{
    return x + 1;
}
```

```sh
nix develop --command -- python3 bench.py \
  --verbose \
  --csv data/2026-08/data.csv \
  --readme README.md \
  --chart data/2026-08/chart.png \
  --toolchain data/2026-08/toolchain.txt \
  --baseline c/static \
  --runs 10 \
  --count 500000000
```

Dart, Wren, and Nim are excluded due to toolchain/skill issues on my part.

# Usage

Requirements:

 - nix w/ flakes enabled

This project includes a Nix flake for reproducible development environments.

## Usage
```sh
# Enter the development shell
nix develop

# Or run commands directly in the development shell
nix develop --command -- ./compile-all.sh
nix develop --command -- ./run-all.sh 500000000
```

The Nix environment includes all required compilers, runtimes, and build tools, including Java versions 8, 21, and 25 in the `vendor/` directory and the flake-built Babashka.

Current environment (Nix) (2026-08):
```text
- x86_64 Linux 6.12.105-fly
- CPU AMD EPYC
# flake inputs
- nixpkgs git 56c02bc00adcf003215cc4bd996d6efaf4cff188
- flakelight git 4d9eabe93ff4d73cc195a0e8dec0f3fbac31c226
- babashka-src git 44bb86e07025391c91dba75c4362e7d6248610b0
- jolt git e8b018cc162cb61c4573f17213cb329c416bd42d
- gcc/g++ 15.3.0
- tup 0.8
- python 3.14.7 (matplotlib 3.11.1, numpy 2.5.1)
- zig 0.16.0
- nim 2.2.10 (disabled - rpath issues)
- v V 0.5.2
- java8 1.8.0_504
- java21 21.0.12
- java25 25.0.4
- go 1.26.5
- rust 1.97.1 (8bab26f4f 2026-07-14) (built from a source tarball)
- dmd 2.112.1
- ldc2 1.42.0
- ghc 9.10.3
- chez 10.4.1
- ocaml 5.4.1
- mono 6.14.1
- sbcl 2.6.7
# dynamic languages
- luajit 2.1.1774638290
- julia 1.12.7
- node 24.19.0
- dart 3.13.0 (disabled - deprecated native extensions)
- wren not available (not in nixpkgs)
- elixir 1.18.4 (Erlang/OTP 28)
- janet 1.41.2-release
- jolt git e8b018c
- clojure 1.12.5 (coffi 1.0.615)
- babashka 1.13.220-SNAPSHOT (git 44bb86e07025391c91dba75c4362e7d6248610b0, libffi 3.8.0, plusone backend trampoline)
```

### Run

```sh
# Run with defaults (2 runs, 500M calls)
nix develop --command -- python3 bench.py --verbose

# Custom parameters
nix develop --command -- python3 bench.py --verbose --runs 5 --count 1000000

# Specify output files
nix develop --command -- python3 bench.py --verbose --csv my_results.csv --readme README.md --chart my_chart.png --toolchain my_toolchain.txt --baseline c/static
```

`--toolchain` regenerates the environment report with available tool versions and
flake-input Git revisions after a successful benchmark run.

`--readme` regenerates the results table from the complete result set and reports
variability as CV (sample standard deviation divided by mean).

### Update one published benchmark

Use `--include` with `--update` to replace one benchmark in an existing dataset
without rerunning the full suite. Other CSV rows are preserved, and the chart is
regenerated from the merged data.

```sh
nix develop --command -- python3 bench.py \
  --verbose \
  --include zig \
  --runs 10 \
  --count 500000000 \
  --csv data/2026-08/data.csv \
  --readme README.md \
  --chart data/2026-08/chart.png \
  --toolchain data/2026-08/toolchain.txt \
  --baseline c/static \
  --update
```

`--update` requires an existing `--csv` file so it cannot accidentally publish a
partial dataset.
