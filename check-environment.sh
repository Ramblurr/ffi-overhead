#!/bin/sh

# Script to report current environment versions like in the README

echo "Current environment:"
echo "\`\`\`"

# System info
echo "- $(uname -m) $(uname -s) $(uname -r)"

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

# Compiled languages
zig_version=$(zig version 2>/dev/null)
if [ -n "$zig_version" ]; then
    echo "- zig $zig_version"
else
    echo "- zig not found"
fi

nim_version=$(nim --version 2>/dev/null | head -1 | cut -d' ' -f4)
if [ -n "$nim_version" ]; then
    echo "- nim $nim_version"
else
    echo "- nim not found"
fi

v_version=$(v version 2>/dev/null | head -1)
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

java24_version=$(./vendor/openjdk24/bin/java -version 2>&1 | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null)
if [ -n "$java24_version" ]; then
    echo "- java24 $java24_version"
else
    echo "- java24 not found"
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

dmd_version=$(dmd --version 2>/dev/null | head -1 | cut -d' ' -f2)
if [ -n "$dmd_version" ]; then
    echo "- dmd $dmd_version"
else
    echo "- dmd not found"
fi

ldc2_version=$(ldc2 --version 2>/dev/null | head -1 | cut -d' ' -f6 | sed 's/[():]//')
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
    echo "- dart $dart_version (disabled - deprecated native extensions)"
else
    echo "- dart not found"
fi

# nim - currently disabled due to rpath issues
nim_version=$(nim --version 2>/dev/null | head -1 | cut -d' ' -f4)
if [ -n "$nim_version" ]; then
    echo "- nim $nim_version (disabled - rpath issues)"
else
    echo "- nim not found"
fi

# wren - not available in nixpkgs
echo "- wren not available (not in nixpkgs)"

elixir_version=$(elixir --version 2>/dev/null | tail -1 | cut -d' ' -f2)
erlang_version=$(elixir --version 2>/dev/null | head -1 | cut -d' ' -f2)
if [ -n "$elixir_version" ] && [ -n "$erlang_version" ]; then
    echo "- elixir $elixir_version (Erlang/OTP $erlang_version)"
else
    echo "- elixir not found"
fi

echo "\`\`\`"