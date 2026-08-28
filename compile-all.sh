#!/bin/sh

# Keep builds under project root
export XDG_CACHE_HOME="$(pwd)/.cache"
export NIMCACHE="$(pwd)/nimcache"

# Set paths for Tupfile
export DART_INCLUDE="$(dirname $(which dart))/../include"
export NODE_INCLUDE="$(dirname $(which node))/../include/node"

tup upd && \
    jolt -Sdeps '{:paths ["jolt"]}' build \
        -m ffi-overhead.jolt -o jolt_hello --opt --direct-link && \
    rm -rf clojure_panama/classes && \
    mkdir -p clojure_panama/classes && \
    clojure -J--enable-native-access=ALL-UNNAMED \
        -Sdeps '{:paths ["." "clojure_panama/classes"]}' \
        -M -e '(binding [*compile-path* "clojure_panama/classes"] (compile (quote clojure-panama.hello)))' && \
    nim c -d:release --parallelBuild:1 --nimcache:nimcache -o:nim_hello --passL:"-Lnewplus -lnewplus -Wl,-rpath,$$ORIGIN/newplus" hello.nim && \
    zig build -Doptimize=ReleaseFast && \
    tup upd && \
    make -C ocaml && \
    make -C elixir

