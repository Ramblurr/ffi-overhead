# Measurement notes

This run uses one machine for every configured benchmark: an AMD Ryzen 9
7950X3D. See `toolchain.txt` for runtime versions and build provenance.
The publication settings are 500,000,000 calls and 10 repetitions, with
`c/static` as the baseline. Each repetition starts a fresh process.

## Babashka

`bb hello.bb COUNT` measures both passes in one process, control first:

1. `run! identity` over a range constructed before timing.
2. `run! plusone` over that same range.

Both passes use the C `current_timestamp` millisecond timer. Argument parsing,
library loading, bindings, callable selection, and range construction happen
outside the timed intervals. Traversal remains inside them; the range is not
materialized as a count-sized collection. No per-call SCI wrapper is used.

The `babashka` row remains the FFI total, including traversal and dispatch.
Its CSV `Babashka samples (JSON)` field retains each invocation's `count`,
`control_ms`, and `ffi_ms` together. Other rows retain their ordinary timing
samples. Additional columns report the mean control and incremental estimates
in milliseconds and ns/call. Babashka-specific fields are empty for other
benchmarks; historical three-column CSVs remain readable.

For each sample:

- Incremental estimate in milliseconds = `ffi_ms - control_ms`.
- Incremental estimate in nanoseconds per call = `(ffi_ms - control_ms) * 1000000 / count`.

The reported estimate averages the paired differences; no differences are
clamped or discarded. Controls and estimates remain in the CSV, console output,
and these notes. The root README and chart show only the ordinary FFI-total row.

This estimates incremental `babashka.ffi` cost for `plusone(int) -> int` on
Babashka 1.13.220 with the observed `trampoline` backend. It is not universal
native-call latency. Borkdude cautioned that realistic FFI usage normally lets
the native library do substantial work, rather than calling a trivial function
hundreds of millions of times.

## Scaling and order checks

`validation.json` contains all validation samples. At each count, each pair of
invocations ran the production control-first script followed by a temporary
copy with just the two measurement bindings reversed. No mode flag or alternate
production runner was added. There were five repetitions per order at 10M and
100M calls, and three per order at 500M calls. Every FFI total exceeded its
control total.

| Calls | Order | Mean FFI (ms) | Mean control (ms) | Mean delta (ns/call) |
|---:|---|---:|---:|---:|
| 10,000,000 | control first | 357.60 | 53.60 | 30.400 |
| 10,000,000 | FFI first | 412.80 | 36.80 | 37.600 |
| 100,000,000 | control first | 3405.20 | 369.40 | 30.358 |
| 100,000,000 | FFI first | 3439.60 | 341.80 | 30.978 |
| 500,000,000 | control first | 16649.00 | 1668.33 | 29.961 |
| 500,000,000 | FFI first | 16703.67 | 1618.00 | 30.171 |

Order affects the short run noticeably: its estimated per-call difference
changes by about 24%. At 100M calls the change is about 2%, and at the 500M
publication count it is about 0.7%. Both totals grow with count, and the
control-first per-call estimate stays near 30 ns. These checks support using
the larger publication count; they do not establish order independence for
shorter workloads.

`smoke.csv` records the successful focused `c/static,babashka` run, with three
repetitions at 10M calls, before the full-suite publication run.

## Publication checks

- All 34 configured benchmarks completed 10 repetitions; none were omitted.
- Babashka averaged 17288.40 ms FFI total, 1661.60 ms control, and 15626.80 ms
  incremental estimate (31.254 ns/call). Every paired difference was positive.
- All 17 Python tests passed, including the real Babashka adapter and traversal
  instrumentation. Black and cljfmt checks passed.
- `nix flake check` passed for x86_64-linux; incompatible architectures were not built.
- The README table and chart regenerated identically from the stored CSV.
- SHA-256 checks confirmed every file in `data/2026-08/` was unchanged.

## Reproduce

From the repository root, in the Nix development shell:

```sh
./compile-all.sh
python3 -m unittest -v test_bench test_babashka
python3 bench.py --include c/static,babashka --baseline c/static \
  --count 10000000 --runs 3 --verbose
python3 bench.py --baseline c/static --count 500000000 --runs 10 --verbose \
  --csv data/2026-09-08/data.csv --chart data/2026-09-08/chart.png \
  --toolchain data/2026-09-08/toolchain.txt --readme README.md
nix flake check
```

Use a new directory for later publications rather than overwriting these files.
The unchanged `data/2026-08/` Babashka row used the old SCI `loop/recur` driver
and includes interpreter overhead. That dataset also mixed machines; it is not
a controlled before/after comparison with this run.
