ffi-overhead
============

comparing the c ffi overhead on various programming languages

# Results (2025-08)

> [!WARNING]  
> I have no idea what I am doing. Do not believe this.

The benchmark results can be visualized using the automated benchmarking harness:

![FFI Overhead Benchmark Results for 2025-08](data/2025-08/chart.png)

*Chart shows average execution times across runs. Lower values are better.*

Raw data: [data/2025-08/raw_data.csv](./data/2025-08/data.csv)

Tool chain versions used: [data/2025-08/toolchain.txt](./data/2025-08/toolchain.txt)

The native function is, ran `count` times

``` c
int plusone(int x)
{
    return x + 1;
}
```

```
❯ ./bench.py --verbose --csv data/2025-08/data.csv --chart ./data/2025-08/chart.png --baseline c/static --runs 10

Benchmark Results (10 runs, count=500,000,000)
───────────────────────────────────────────────────────────────────────────────
│ Benchmark     │     Mean │      Min │      Max │  Std Dev │     vs Baseline │
───────────────────────────────────────────────────────────────────────────────
│ c/static      │   486 ms │   474 ms │   495 ms │   5.9 ms │ 1.00x (baseline) │
│ luajit        │   764 ms │   753 ms │   773 ms │   6.6 ms │    1.57x slower │
│ c/dynamic     │   871 ms │   853 ms │   954 ms │  31.1 ms │    1.79x slower │
│ cpp           │   885 ms │   851 ms │   953 ms │  29.3 ms │    1.82x slower │
│ CL/SBCL       │  1180 ms │  1149 ms │  1199 ms │  15.3 ms │    2.43x slower │
│ zig           │   485 ms │   478 ms │   493 ms │   5.0 ms │    1.00x faster │
│ v             │   583 ms │   573 ms │   593 ms │   6.2 ms │    1.20x slower │
│ rust          │   772 ms │   765 ms │   779 ms │   4.4 ms │    1.59x slower │
│ d             │   889 ms │   859 ms │   968 ms │  34.5 ms │    1.83x slower │
│ d ldc2        │   904 ms │   866 ms │   951 ms │  37.7 ms │    1.86x slower │
│ haskell       │   879 ms │   848 ms │   944 ms │  34.0 ms │    1.81x slower │
│ ocamlopt      │   868 ms │   848 ms │   884 ms │  11.2 ms │    1.79x slower │
│ ocamlc        │  2679 ms │  2636 ms │  2817 ms │  54.2 ms │    5.52x slower │
│ csharp mono   │ 18446 ms │ 18291 ms │ 18542 ms │  84.7 ms │   37.99x slower │
│ java8/jni     │  1486 ms │  1450 ms │  1638 ms │  55.6 ms │    3.06x slower │
│ java21/jni    │  1658 ms │  1633 ms │  1692 ms │  15.3 ms │    3.42x slower │
│ java24/jni    │  1655 ms │  1641 ms │  1669 ms │   9.3 ms │    3.41x slower │
│ java21/panama │  1301 ms │  1289 ms │  1307 ms │   6.0 ms │    2.68x slower │
│ java24/panama │  1399 ms │  1368 ms │  1464 ms │  28.6 ms │    2.88x slower │
│ node          │  3947 ms │  3846 ms │  4278 ms │ 123.1 ms │    8.13x slower │
│ go            │ 12612 ms │ 12532 ms │ 12711 ms │  65.5 ms │   25.98x slower │
│ elixir        │  8338 ms │  8222 ms │  8435 ms │  74.2 ms │   17.17x slower │
│ julia         │   480 ms │   471 ms │   485 ms │   4.8 ms │    1.01x faster │
│ janet         │ 24720 ms │ 24411 ms │ 24996 ms │ 171.9 ms │   50.92x slower │
│ clj/coffi     │  2636 ms │  2591 ms │  2803 ms │  62.2 ms │    5.43x slower │
───────────────────────────────────────────────────────────────────────────────
```

Ran on a AMD Ryzen 9 7950X3D 16-Core cpu

I disabled dart, wren, and nim because I couldn't get them working after
banging on it for about an hour, and (sorry not sorry) I don't care so much to
fix them.


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
- janet 1.38.0-release
- clojure 1.12.1 (coffi 1.0.615)
- nim 2.2.4 (disabled - rpath issues)
- dart 3.8.2 (disabled - deprecated native extensions)
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
