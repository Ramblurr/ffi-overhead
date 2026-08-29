# ClojureDart FFI benchmark

This benchmark is adapted from the ClojureDart FFI sample in
`cljd_hello/ffi`. It binds the repository's `plusone` and `current_timestamp`
symbols with typed `DynamicLibrary.lookupFunction` calls. It builds both an
`isLeaf: true` variant and a normal non-leaf variant.

The Tup build compiles the ClojureDart source to Dart in a temporary project,
then produces these benchmark artifacts:

- `cljd_ffi_nonleaf.dill`: JIT, normal non-leaf FFI (`cljd/ffi/jit`)
- `cljd_ffi_leaf.dill`: JIT with `isLeaf: true` (`cljd/ffi/jit/leaf`)
- `cljd_ffi_nonleaf_hello`: AOT, normal non-leaf FFI (`cljd/ffi/aot`)
- `cljd_ffi_hello`: AOT with `isLeaf: true` (`cljd/ffi/aot/leaf`)
