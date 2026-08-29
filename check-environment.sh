#!/usr/bin/env bash

echo "Current environment:"
echo "\`\`\`"

# System info
echo "- $(uname -m) $(uname -s) $(uname -r)"
cpu_model=$(sed -n 's/^model name[[:space:]]*: //p' /proc/cpuinfo | head -1)
echo "- CPU $cpu_model"

echo "# flake inputs"
python3 <<'PY'
import json

with open("flake.lock") as f:
    nodes = json.load(f)["nodes"]

for name in ("nixpkgs", "flakelight", "babashka-src", "jolt"):
    locked = nodes[name]["locked"]
    print(f"- {name} git {locked['rev']}")
PY

# Build tools
gcc_version=$(gcc --version 2>/dev/null | head -1 | sed 's/.*) //')
if [ -n "$gcc_version" ]; then
    echo "- gcc/g++ $gcc_version"
else
    echo "- gcc/g++ not found"
fi

tup_version=$(tup --version 2>/dev/null | head -1)
if [ -n "$tup_version" ]; then
    echo "- $tup_version"
else
    echo "- tup not found"
fi

python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
matplotlib_version=$(python3 -c 'import matplotlib; print(matplotlib.__version__)' 2>/dev/null)
numpy_version=$(python3 -c 'import numpy; print(numpy.__version__)' 2>/dev/null)
echo "- python $python_version (matplotlib $matplotlib_version, numpy $numpy_version)"

# Compiled languages
zig_version=$(zig version 2>/dev/null)
if [ -n "$zig_version" ]; then
    echo "- zig $zig_version"
else
    echo "- zig not found"
fi

nim_version=$(nim --version 2>/dev/null | head -1 | cut -d' ' -f4)
if [ -n "$nim_version" ]; then
    echo "- nim $nim_version (disabled - rpath issues)"
else
    echo "- nim not found"
fi

v_version=$(v version 2>/dev/null | head -1 | sed 's/[[:space:]]*$//')
if [ -n "$v_version" ]; then
    echo "- v $v_version"
else
    echo "- v not found"
fi

# Check for Java versions
java8_version=$(./vendor/openjdk8/bin/java -version 2>&1 | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null)
if [ -n "$java8_version" ]; then
    echo "- java8 $java8_version"
else
    echo "- java8 not found"
fi

java21_version=$(./vendor/openjdk21/bin/java -version 2>&1 | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null)
if [ -n "$java21_version" ]; then
    echo "- java21 $java21_version"
else
    echo "- java21 not found"
fi

java25_version=$(./vendor/openjdk25/bin/java -version 2>&1 | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null)
if [ -n "$java25_version" ]; then
    echo "- java25 $java25_version"
else
    echo "- java25 not found"
fi

go_version=$(go version 2>/dev/null | cut -d' ' -f3 | sed 's/go//')
if [ -n "$go_version" ]; then
    echo "- go $go_version"
else
    echo "- go not found"
fi

rust_version=$(rustc --version 2>/dev/null | cut -d' ' -f2-)
if [ -n "$rust_version" ]; then
    echo "- rust $rust_version"
else
    echo "- rust not found"
fi

dmd_version=$(dmd --version 2>/dev/null | head -1 | sed -n 's/.*Compiler v\([^ ]*\).*/\1/p')
if [ -n "$dmd_version" ]; then
    echo "- dmd $dmd_version"
else
    echo "- dmd not found"
fi

ldc2_version=$(ldc2 --version 2>/dev/null | head -1 | sed -n 's/.*(\([^):]*\)).*/\1/p')
if [ -n "$ldc2_version" ]; then
    echo "- ldc2 $ldc2_version"
else
    echo "- ldc2 not found"
fi

ghc_version=$(ghc --version 2>/dev/null | cut -d' ' -f8)
if [ -n "$ghc_version" ]; then
    echo "- ghc $ghc_version"
else
    echo "- ghc not found"
fi

chez_version=$(scheme --version 2>/dev/null)
if [ -n "$chez_version" ]; then
    echo "- chez $chez_version"
else
    echo "- chez not found"
fi

ocaml_version=$(ocaml -version 2>/dev/null | cut -d' ' -f5)
if [ -n "$ocaml_version" ]; then
    echo "- ocaml $ocaml_version"
else
    echo "- ocaml not found"
fi

mono_version=$(mono --version 2>/dev/null | head -1 | cut -d' ' -f5)
if [ -n "$mono_version" ]; then
    echo "- mono $mono_version"
else
    echo "- mono not found"
fi

sbcl_version=$(sbcl --version 2>/dev/null | cut -d' ' -f2)
if [ -n "$sbcl_version" ]; then
    echo "- sbcl $sbcl_version"
else
    echo "- sbcl not found"
fi

echo "# dynamic languages"

luajit_version=$(luajit -v 2>/dev/null | head -1 | cut -d' ' -f2)
if [ -n "$luajit_version" ]; then
    echo "- luajit $luajit_version"
else
    echo "- luajit not found"
fi

julia_version=$(julia --version 2>/dev/null | cut -d' ' -f3)
if [ -n "$julia_version" ]; then
    echo "- julia $julia_version"
else
    echo "- julia not found"
fi

node_version=$(node --version 2>/dev/null | sed 's/v//')
if [ -n "$node_version" ]; then
    echo "- node $node_version"
else
    echo "- node not found"
fi

dart_version=$(dart --version 2>&1 | head -1 | sed 's/Dart SDK version: //' | cut -d' ' -f1)
if [ -n "$dart_version" ]; then
    echo "- dart $dart_version"
else
    echo "- dart not found"
fi

# wren - not available in nixpkgs
echo "- wren not available (not in nixpkgs)"

elixir_output=$(elixir --version 2>/dev/null)
elixir_version=$(printf '%s\n' "$elixir_output" | sed -n 's/^Elixir \([^ ]*\).*/\1/p')
erlang_version=$(printf '%s\n' "$elixir_output" | sed -n 's/^Erlang\/OTP \([^ ]*\).*/\1/p')
if [ -n "$elixir_version" ] && [ -n "$erlang_version" ]; then
    echo "- elixir $elixir_version (Erlang/OTP $erlang_version)"
else
    echo "- elixir not found"
fi

janet_version=$(janet --version 2>/dev/null)
if [ -n "$janet_version" ]; then
    echo "- janet $janet_version"
else
    echo "- janet not found"
fi

jolt_identifier=$(jolt --version 2>/dev/null | sed 's/^jolt //')
if [ -n "$jolt_identifier" ]; then
    if printf '%s\n' "$jolt_identifier" | grep -Eq '^[0-9a-f]{7,40}$'; then
        echo "- jolt git $jolt_identifier"
    else
        echo "- jolt $jolt_identifier"
    fi
else
    echo "- jolt not found"
fi
clojure_version=$(clj -M -e '(clojure-version)' 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
if [ -n "$clojure_version" ]; then
    coffi_version=$(sed -n 's/.*org\.suskalo\/coffi {:mvn\/version "\([^"]*\)".*/\1/p' clojure_coffi/deps.edn)
    echo "- clojure $clojure_version (coffi $coffi_version)"
fi

bb_version=$(bb --version 2>/dev/null | sed 's/^babashka v//')
bb_description=$(bb describe 2>/dev/null)
bb_sha=$(printf '%s\n' "$bb_description" | sed -n 's/.*:git\/sha[[:space:]]*"\([^"]*\)".*/\1/p')
bb_libffi=$(printf '%s\n' "$bb_description" | sed -n 's/.*:libffi\/version[[:space:]]*"\([^"]*\)".*/\1/p')
bb_backend=$(bb -e '(require (quote [babashka.ffi :as ffi])) (let [library (ffi/load-library "./newplus/libnewplus.so") plusone (ffi/cfn library "plusone" [:int] :int)] (println (name (:babashka.ffi/backend (meta plusone)))))' 2>/dev/null)
echo "- babashka $bb_version (git $bb_sha, libffi $bb_libffi, plusone backend $bb_backend)"

echo "\`\`\`"
