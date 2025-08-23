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
nix develop --command -- python3 bench.py

# Custom parameters
nix develop --command -- python3 bench.py --runs 5 --count 1000000

# Specify output files
nix develop --command -- python3 bench.py --csv my_results.csv --chart my_chart.png
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
