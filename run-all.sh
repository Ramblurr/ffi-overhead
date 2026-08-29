#!/usr/bin/env bash

[ $# -gt 0 ] || { echo "First arg (0 - 2000000000) is required."; exit 1; }

[ "$1" -eq "$1" ] 2>/dev/null || { echo "Must be a positive number not exceeding 2 billion."; exit 1; }

echo "The results are elapsed time in milliseconds"
echo "============================================"

if [ "$2" = "scoped" ]; then
    echo -e "\nnode scoped:"
    node hello.js $@ && \
    node hello.js $@

    exit 0
fi

echo -e "\nluajit:"
luajit hello.lua $@ && \
luajit hello.lua $@

echo -e "\nc:"
./c_hello $@ && \
./c_hello $@

echo -e "\ncpp:"
./cpp_hello $@ && \
./cpp_hello $@

echo -e "\nCommon Lisp via SBCL:"
sbcl --script hello.lisp $@ && \
sbcl --script hello.lisp $@

echo -e "\nzig:"
./zig-out/zig_hello/zig_hello $@ && \
./zig-out/zig_hello/zig_hello $@

# echo -e "\nnim:"
# ./nim_hello $@ && \
# ./nim_hello $@

echo -e "\nv:"
./v_hello $@ && \
./v_hello $@

echo -e "\nrust:"
./rust_hello $@ && \
./rust_hello $@

echo -e "\nd:"
./d_hello $@ && \
./d_hello $@

echo -e "\nd ldc2:"
./d_ldc2_hello $@ && \
./d_ldc2_hello $@

echo -e "\nhaskell:"
./ghc_hello $@ && \
./ghc_hello $@

echo -e "\nocamlopt:"
./ocaml/test.nat $@ && \
./ocaml/test.nat $@

echo -e "\nocamlc:"
./ocaml/test.bc $@ && \
./ocaml/test.bc $@

# TODO: CoreCLR and natively running on Windows
echo -e "\ncsharp mono:"
mono ./csharp_hello.exe $@ && \
mono ./csharp_hello.exe $@

echo -e "\njava8:"
./vendor/openjdk8/bin/java -cp . jhello.Hello $@ && \
./vendor/openjdk8/bin/java -cp . jhello.Hello $@

echo -e "\njava21:"
./vendor/openjdk21/bin/java --enable-native-access=ALL-UNNAMED -cp jhello21 jhello.Hello $@ && \
./vendor/openjdk21/bin/java --enable-native-access=ALL-UNNAMED -cp jhello21 jhello.Hello $@

echo -e "\njava25:"
./vendor/openjdk25/bin/java --enable-native-access=ALL-UNNAMED -cp jhello25 jhello.Hello $@ && \
./vendor/openjdk25/bin/java --enable-native-access=ALL-UNNAMED -cp jhello25 jhello.Hello $@

echo -e "\njava21 panama:"
./vendor/openjdk21/bin/java --enable-preview --enable-native-access=ALL-UNNAMED -cp . jhello_panama.Hello $@ && \
./vendor/openjdk21/bin/java --enable-preview --enable-native-access=ALL-UNNAMED -cp . jhello_panama.Hello $@

echo -e "\njava25 panama:"
./vendor/openjdk25/bin/java --enable-native-access=ALL-UNNAMED -cp jhello_panama25 jhello_panama.Hello $@ && \
./vendor/openjdk25/bin/java --enable-native-access=ALL-UNNAMED -cp jhello_panama25 jhello_panama.Hello $@

echo -e "\nnode:"
node hello.js $@ && \
node hello.js $@

echo -e "\ngo:"
./go_hello $@ && \
./go_hello $@

echo -e "\ndart:"
dart hello.dart $@ && \
dart hello.dart $@

# echo -e "\nwren:"
# ./wren_hello hello.wren $@ && \
# ./wren_hello hello.wren $@

echo -e "\nelixir:"
elixir -r hello.ex -e "S.start" $@ && \
elixir -r hello.ex -e "S.start" $@

echo -e "\njulia:"
julia hello.jl $@ && \
julia hello.jl $@

echo -e "\njanet:"
janet hello.janet $@ && \
janet hello.janet $@

