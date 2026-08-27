{
  description = "dev env";
  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1"; # tracks nixpkgs unstable branch
    # TODO remove once babashka with ffi ends up in nixpkgs
    babashka-src = {
      url = "git+https://github.com/babashka/babashka.git?submodules=1";
      flake = false;
    };
    jolt = {
      url = "git+https://github.com/jolt-lang/jolt.git?submodules=1";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flakelight.url = "github:nix-community/flakelight";
    flakelight.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs =
    {
      self,
      babashka-src,
      flakelight,
      jolt,
      nixpkgs,
      ...
    }:
    let
      makeBabashka =
        pkgs:
        let
          version = builtins.replaceStrings [ "\n" ] [ "" ] (
            builtins.readFile "${babashka-src}/resources/BABASHKA_VERSION"
          );
          libffiStatic = pkgs.libffi.overrideAttrs (old: {
            version = "3.8.0";
            src = pkgs.fetchurl {
              url = "https://github.com/libffi/libffi/releases/download/v3.8.0/libffi-3.8.0.tar.gz";
              hash = "sha256-faPi2aFx6woDj1kuytP/K7JVDzSW2Hs7Ka0M9EMMDbQ=";
            };
            dontDisableStatic = true;
            configureFlags = (old.configureFlags or [ ]) ++ [ "--disable-shared" ];
            doCheck = false;
          });
          standaloneJar = pkgs.stdenvNoCC.mkDerivation {
            pname = "babashka-standalone";
            inherit version;
            src = babashka-src;
            nativeBuildInputs = [
              pkgs.graalvmPackages.graalvm-ce
              pkgs.git
              pkgs.leiningen
            ];
            env = {
              GRAALVM_HOME = pkgs.graalvmPackages.graalvm-ce;
              BABASHKA_LIBFFI = "${libffiStatic}/lib/libffi.a";
              BABASHKA_FEATURE_LIBFFI = "true";
            };
            SOURCE_DATE_EPOCH = babashka-src.lastModified;
            buildPhase = ''
              runHook preBuild
              patchShebangs script
              export HOME="$TMPDIR"
              script/uberjar
              runHook postBuild
            '';
            installPhase = ''
              runHook preInstall
              mkdir -p "$out"
              install -m444 "target/babashka-${version}-standalone.jar" "$out/babashka.jar"
              install -m444 target/metabom.jar "$out/metabom.jar"
              runHook postInstall
            '';
            outputHashMode = "recursive";
            outputHashAlgo = "sha256";
            outputHash = "sha256-wRGMofM1bJBTtjXxm2mLXvvv+y66vZfOTVmat+hLg7E=";
          };
          unwrapped = pkgs.babashka-unwrapped.overrideAttrs (old: {
            inherit version;
            src = "${standaloneJar}/babashka.jar";
            preBuild = (old.preBuild or "") + ''
              cp ${standaloneJar}/metabom.jar .
            '';
            nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ libffiStatic ];
            env = (old.env or { }) // {
              BABASHKA_FEATURE_LIBFFI = "true";
              BABASHKA_SHA = babashka-src.rev;
            };
            nativeImageArgs = (old.nativeImageArgs or [ ]) ++ [
              "-EBABASHKA_FEATURE_LIBFFI"
              "-EBABASHKA_SHA"
              "--future-defaults=all"
              "-H:NativeLinkerOption=-Wl,--whole-archive,${libffiStatic}/lib/libffi.a,--no-whole-archive"
            ];
          });
          wrapped = pkgs.babashka.override {
            babashka-unwrapped = unwrapped;
            clojureToolsBabashka = pkgs.clojure;
            jdkBabashka = pkgs.clojure.jdk;
          };
        in
        wrapped.overrideAttrs (old: {
          nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ pkgs.gcc ];
          installCheckPhase = (old.installCheckPhase or "") + ''
            describe="$($out/bin/bb describe)"
            echo "$describe" | grep -F '"${babashka-src.rev}"'
            echo "$describe" | grep -E ':libffi/version[[:space:]]+"[^"[:space:]]+"'

            cc -shared -fPIC -I${./newplus} ${./newplus/plus.c} -o libnewplus.so
            cat > ffi-check.clj <<'EOF'
            (require '[babashka.ffi :as ffi])
            (def library (ffi/load-library "./libnewplus.so"))
            (def plusone (ffi/cfn library "plusone" [:int] :int))
            (assert (= 42 (plusone 41)))
            (assert (= :trampoline (:babashka.ffi/backend (meta plusone))))
            EOF
            $out/bin/bb ffi-check.clj
          '';
        });
    in
    flakelight ./. {
      packages = { system, ... }: {
        babashka-git = _: makeBabashka nixpkgs.legacyPackages.${system};
      };
      devShell =
        pkgs:
        let
          javaVersion = "25";
          jdk = pkgs."jdk${javaVersion}";
          clojure = pkgs.clojure.override { inherit jdk; };
          libraries = [
            # Add any libraries needed for LD_LIBRARY_PATH here
          ];
        in
        {
          packages = [
            (makeBabashka nixpkgs.legacyPackages.${pkgs.stdenv.hostPlatform.system})
            jolt.packages.${pkgs.stdenv.hostPlatform.system}.default
            clojure
            # Build tools
            pkgs.gcc
            pkgs.gnumake
            pkgs.tup
            pkgs.jet
            # Language compilers and runtimes
            pkgs.nim
            pkgs.zig_0_16
            pkgs.go
            pkgs.rustc
            pkgs.cargo
            pkgs.dmd
            pkgs.ldc
            pkgs.ghc
            pkgs.ocaml
            pkgs.mono
            pkgs.nodejs
            pkgs.node-gyp
            pkgs.python3
            pkgs.python3Packages.matplotlib
            pkgs.python3Packages.numpy
            pkgs.dart
            pkgs.luajit
            pkgs.julia
            pkgs.beamPackages.elixir
            pkgs.beamPackages.erlang
            pkgs.vlang
            pkgs.sbcl
            pkgs.janet
          ];
          env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath libraries;
          # example pkg config path setting
          #env.PKG_CONFIG_PATH = "${h2o-static}/lib/pkgconfig:${clj-h2o-shim}/lib/pkgconfig";
          shellHook = ''
            mkdir -p vendor
            ln -sfn ${pkgs.jdk8} vendor/openjdk8 || true
            ln -sfn ${pkgs.jdk11} vendor/openjdk11 || true
            ln -sfn ${pkgs.jdk17} vendor/openjdk17 || true
            ln -sfn ${pkgs.jdk21} vendor/openjdk21 || true
            ln -sfn ${pkgs.jdk25} vendor/openjdk25 || true
            ln -sfn ${pkgs.nodejs} vendor/nodejs || true
            ln -sfn ${pkgs.dart} vendor/dart || true

          '';

        };

      flakelight.builtinFormatters = false;
      formatters = pkgs: {
        "*.nix" = "${pkgs.nixfmt}/bin/nixfmt";
        "*.clj" = "${pkgs.cljfmt}/bin/cljfmt fix";
      };

    };
}
