ffi-overhead
============

comparing the c ffi overhead on various programming languages

Requirements:
- gcc
- tup
- zig
- nim
- v
- java7
- java8
- go
- rust
- d (dmd and ldc2)
- haskell (ghc)
- ocaml
- csharp (mono)
- luajit
- julia
- node
- dart
- wren
- elixir

## Nix Development Environment

This project includes a Nix flake for reproducible development environments. To use it:

### Prerequisites
- Install Nix with flakes enabled

### Usage
```sh
# Enter the development shell
nix develop

# Or run commands directly in the development shell
nix develop --command -- ./compile-all.sh
nix develop --command -- ./run-all.sh 500000000
```

The Nix environment includes all required compilers, runtimes, and build tools, including multiple Java versions (8, 21, 24) in the `vendor/` directory.

Current environment (Nix) (2025-08):
```
- x86_64 Linux 6.12.41
- gcc/g++ 14.3.0
- tup 0.8
- zig 0.14.1
- nim 2.2.4
- v V 0.4.11
- java8 1.8.0_462
- java21 21.0.7
- java24 24.0.2
- go 1.24.5
- rust 1.88.0 (6b00bc388 2025-06-23) (built from a source tarball)
- dmd D
- ldc2 compiler
- ghc 9.8.4
- ocaml 5.3.0
- mono 6.14.1
- sbcl 2.5.5
# dynamic languages
- luajit 2.1.1741730670
- julia 1.11.6
- node 22.17.0
- elixir 1.18.4 (Erlang/OTP 27)
- janet 1.38.0-release
- clojure 1.12.1 (coffi 1.0.615)
- nim 2.2.4 (disabled - rpath issues)
- dart 3.8.2 (disabled - deprecated native extensions)
- wren not available (not in nixpkgs)
```

### Initialize
```sh
nix develop --command -- tup init
```

### Compile
```sh
nix develop --command -- ./compile-all.sh
```

Compile opts:
- -O2 (gcc - applies to c/jni/nim)
- -C opt-level=2 (rust)

### Run

```sh
# Run with defaults (2 runs, 500M calls)
nix develop --command -- python3 bench.py --verbose

# Custom parameters
nix develop --command -- python3 bench.py --verbose --runs 5 --count 1000000

# Specify output files
nix develop --command -- python3 bench.py --verbose --csv my_results.csv --chart my_chart.png
```

The harness will:
- Run benchmarks multiple times and average the results
- Generate a CSV file with detailed timing data
- Create a bar chart visualization (PNG format)
- Print a summary of results sorted by performance

Measurement:
- call the c function "plusone" x number of times and print out the elapsed time in millis.
 ```c
int x = 0;
while (x < count) x = plusone(x);
 ```


Default run is with 2 samples

## Results (500M calls)

The benchmark results can be visualized using the automated benchmarking harness:

![FFI Overhead Benchmark Results for 2025-08](data/2025-08/chart.png)

*Chart shows average execution times across multiple runs. Lower values indicate better performance.*

Raw data: [data/2025-08/raw_data.csv](./data/2025-08/data.csv)

Tool chain versions used: [data/2025-08/toolchain.txt](./data/2025-08/toolchain.txt)


```
❯ ./bench.py --verbose --csv data/2025-08/data.csv --chart ./data/2025-08/chart.png --baseline c

Benchmark Results (2 runs, count=500,000,000)
───────────────────────────────────────────────────────────────────────────────
│ Benchmark     │     Mean │      Min │      Max │  Std Dev │     vs Baseline │
───────────────────────────────────────────────────────────────────────────────
│ c             │   892 ms │   863 ms │   920 ms │  40.3 ms │ 1.00x (baseline) │
│ luajit        │   753 ms │   752 ms │   754 ms │   1.4 ms │    1.18x faster │
│ cpp           │   860 ms │   848 ms │   872 ms │  17.0 ms │    1.04x faster │
│ CL/SBCL       │  1148 ms │  1144 ms │  1151 ms │   4.9 ms │    1.29x slower │
│ zig           │   483 ms │   483 ms │   483 ms │   0.0 ms │    1.85x faster │
│ v             │     0 ms │     0 ms │     0 ms │   0.0 ms │ N/A (mean ~0ms) │
│ rust          │   761 ms │   760 ms │   762 ms │   1.4 ms │    1.17x faster │
│ d             │   852 ms │   847 ms │   857 ms │   7.1 ms │    1.05x faster │
│ d ldc2        │   860 ms │   857 ms │   863 ms │   4.2 ms │    1.04x faster │
│ haskell       │     0 ms │     0 ms │     0 ms │   0.0 ms │ N/A (mean ~0ms) │
│ ocamlopt      │   878 ms │   874 ms │   882 ms │   5.7 ms │    1.02x faster │
│ ocamlc        │  2596 ms │  2591 ms │  2602 ms │   7.8 ms │    2.91x slower │
│ csharp mono   │ 18222 ms │ 18218 ms │ 18226 ms │   5.7 ms │   20.44x slower │
│ java8/jni     │  1456 ms │  1438 ms │  1474 ms │  25.5 ms │    1.63x slower │
│ java21/jni    │  1648 ms │  1646 ms │  1651 ms │   3.5 ms │    1.85x slower │
│ java24/jni    │  1670 ms │  1665 ms │  1674 ms │   6.4 ms │    1.87x slower │
│ java21/panama │  1328 ms │  1297 ms │  1360 ms │  44.5 ms │    1.49x slower │
│ java24/panama │  1395 ms │  1372 ms │  1418 ms │  32.5 ms │    1.56x slower │
│ node          │  3894 ms │  3867 ms │  3920 ms │  37.5 ms │    4.37x slower │
│ go            │ 12222 ms │ 12175 ms │ 12268 ms │  65.8 ms │   13.71x slower │
│ elixir        │  8168 ms │  8136 ms │  8199 ms │  44.5 ms │    9.16x slower │
│ julia         │   476 ms │   475 ms │   476 ms │   0.7 ms │    1.87x faster │
│ janet         │ 24342 ms │ 24335 ms │ 24348 ms │   9.2 ms │   27.30x slower │
│ clj/coffi     │  2606 ms │  2581 ms │  2631 ms │  35.4 ms │    2.92x slower │
───────────────────────────────────────────────────────────────────────────────
```
