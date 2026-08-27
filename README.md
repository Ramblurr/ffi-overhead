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
| c/static | 487 ms | 479 ms | 492 ms | 4.5 ms | 1.00x (baseline) |
| luajit | 1368 ms | 1319 ms | 1402 ms | 31.4 ms | 2.81x slower |
| c/dynamic | 903 ms | 891 ms | 946 ms | 15.8 ms | 1.86x slower |
| cpp | 920 ms | 900 ms | 990 ms | 27.7 ms | 1.89x slower |
| CL/SBCL | 1196 ms | 1172 ms | 1231 ms | 19.4 ms | 2.46x slower |
| zig | 497 ms | 490 ms | 506 ms | 5.2 ms | 1.02x slower |
| v | 803 ms | 790 ms | 819 ms | 9.1 ms | 1.65x slower |
| rust | 807 ms | 794 ms | 824 ms | 8.9 ms | 1.66x slower |
| d | 912 ms | 899 ms | 931 ms | 10.0 ms | 1.87x slower |
| d ldc2 | 912 ms | 905 ms | 933 ms | 8.6 ms | 1.87x slower |
| haskell | 910 ms | 900 ms | 915 ms | 4.9 ms | 1.87x slower |
| ocamlopt | 905 ms | 895 ms | 920 ms | 8.6 ms | 1.86x slower |
| ocamlc | 2551 ms | 2507 ms | 2622 ms | 34.0 ms | 5.24x slower |
| csharp mono | 20031 ms | 19906 ms | 20161 ms | 84.2 ms | 41.16x slower |
| java8/jni | 1574 ms | 1484 ms | 1776 ms | 84.3 ms | 3.23x slower |
| java21/jni | 1626 ms | 1602 ms | 1656 ms | 15.6 ms | 3.34x slower |
| java25/jni | 1602 ms | 1567 ms | 1706 ms | 42.1 ms | 3.29x slower |
| java21/panama | 1468 ms | 1431 ms | 1529 ms | 26.7 ms | 3.02x slower |
| java25/panama | 1424 ms | 1390 ms | 1469 ms | 25.2 ms | 2.93x slower |
| node | 3903 ms | 3775 ms | 4351 ms | 163.5 ms | 8.02x slower |
| go | 10363 ms | 9747 ms | 11204 ms | 467.8 ms | 21.29x slower |
| elixir | 9452 ms | 9179 ms | 10088 ms | 297.4 ms | 19.42x slower |
| julia | 515 ms | 503 ms | 525 ms | 7.0 ms | 1.06x slower |
| janet | 28320 ms | 27211 ms | 34228 ms | 2101.6 ms | 58.19x slower |
| jolt | 4847 ms | 4698 ms | 5061 ms | 95.5 ms | 9.96x slower |
| babashka | 32304 ms | 31286 ms | 33552 ms | 690.7 ms | 66.37x slower |
| clj/coffi | 2872 ms | 2707 ms | 3083 ms | 130.1 ms | 5.90x slower |

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
- jolt aafa0fc
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
