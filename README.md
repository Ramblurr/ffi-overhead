ffi-overhead
============

comparing the c ffi overhead on various programming languages

# Results (2026-08)

> [!WARNING]
> I have no idea what I am doing. Do not believe this.

![FFI Overhead Benchmark Results for 2026-08](data/2026-08/chart.png)

*Chart shows average execution times across 10 runs. Lower values are better.*

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
  --chart data/2026-08/chart.png \
  --baseline c/static \
  --runs 10 \
  --count 500000000
```

| Benchmark | Mean | Min | Max | Std dev | vs baseline |
|---|---:|---:|---:|---:|---:|
| c/static | 502 ms | 497 ms | 506 ms | 2.6 ms | 1.00x (baseline) |
| luajit | 1361 ms | 1351 ms | 1379 ms | 8.2 ms | 2.71x slower |
| c/dynamic | 905 ms | 890 ms | 983 ms | 27.9 ms | 1.80x slower |
| cpp | 894 ms | 887 ms | 932 ms | 14.3 ms | 1.78x slower |
| CL/SBCL | 1190 ms | 1182 ms | 1205 ms | 7.5 ms | 2.37x slower |
| zig | 496 ms | 494 ms | 498 ms | 1.4 ms | 1.01x faster |
| v | 792 ms | 789 ms | 797 ms | 2.4 ms | 1.58x slower |
| rust | 786 ms | 783 ms | 792 ms | 3.2 ms | 1.57x slower |
| d | 892 ms | 883 ms | 900 ms | 5.4 ms | 1.77x slower |
| d ldc2 | 892 ms | 887 ms | 913 ms | 7.6 ms | 1.78x slower |
| haskell | 896 ms | 886 ms | 940 ms | 15.8 ms | 1.78x slower |
| ocamlopt | 897 ms | 892 ms | 902 ms | 3.7 ms | 1.79x slower |
| ocamlc | 2516 ms | 2491 ms | 2547 ms | 18.8 ms | 5.01x slower |
| csharp mono | 19776 ms | 19667 ms | 19938 ms | 97.8 ms | 39.36x slower |
| java8/jni | 1549 ms | 1491 ms | 1866 ms | 118.2 ms | 3.08x slower |
| java21/jni | 1636 ms | 1576 ms | 1823 ms | 73.5 ms | 3.26x slower |
| java25/jni | 1592 ms | 1551 ms | 1620 ms | 18.3 ms | 3.17x slower |
| java21/panama | 1450 ms | 1436 ms | 1490 ms | 16.5 ms | 2.89x slower |
| java25/panama | 1580 ms | 1435 ms | 1768 ms | 125.2 ms | 3.14x slower |
| node | 3963 ms | 3824 ms | 4297 ms | 163.8 ms | 7.89x slower |
| go | 9904 ms | 9675 ms | 10206 ms | 183.5 ms | 19.71x slower |
| elixir | 8564 ms | 8474 ms | 8631 ms | 52.9 ms | 17.05x slower |
| julia | 500 ms | 495 ms | 503 ms | 2.7 ms | 1.01x faster |
| janet | 26997 ms | 26452 ms | 28058 ms | 449.6 ms | 53.74x slower |
| babashka | 31653 ms | 31110 ms | 32282 ms | 387.0 ms | 63.00x slower |
| clj/coffi | 2873 ms | 2685 ms | 3330 ms | 189.9 ms | 5.72x slower |

Ran on an AMD Ryzen 9 7950X3D 16-Core CPU.

Babashka's fixed `[:int] -> :int` binding uses its compiled `:trampoline` backend. The binary was built from upstream Git with Java FFM support and linked libffi 3.8.0 fallback support.

Dart, Wren, and Nim remain excluded from the published benchmark population.

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
- x86_64 Linux 6.18.39
- CPU AMD Ryzen 9 7950X3D 16-Core Processor
- gcc/g++ 15.3.0
- tup 0.8
- python 3.14.7 (matplotlib 3.11.1, numpy 2.5.1)
- zig 0.14.1
- v V 0.5.2
- java8 1.8.0_504
- java21 21.0.12
- java25 25.0.4
- go 1.26.5
- rust 1.97.1
- dmd 2.112.1
- ldc2 1.42.0
- ghc 9.10.3
- ocaml 5.4.1
- mono 6.14.1
- sbcl 2.6.7
# dynamic languages
- luajit 2.1.1774638290
- julia 1.12.7
- node 24.19.0
- elixir 1.18.4 (Erlang/OTP 28)
- janet 1.41.2-release
- clojure 1.12.5 (coffi 1.0.615)
- babashka 1.13.220-SNAPSHOT (libffi 3.8.0, plusone backend trampoline)
- nim 2.2.10 (disabled - rpath issues)
- dart 3.13.0 (disabled - deprecated native extensions)
- wren not available (not in nixpkgs)
```

### Run

```sh
# Run with defaults (2 runs, 500M calls)
nix develop --command -- python3 bench.py --verbose

# Custom parameters
nix develop --command -- python3 bench.py --verbose --runs 5 --count 1000000

# Specify output files
nix develop --command -- python3 bench.py --verbose --csv my_results.csv --chart my_chart.png
```
