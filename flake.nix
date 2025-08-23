{
  description = "dev env";
  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1"; # tracks nixpkgs unstable branch
    flakelight.url = "github:nix-community/flakelight";
    flakelight.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs =
    {
      self,
      flakelight,
      ...
    }:
    flakelight ./. {
      devShell =
        pkgs:
        let
          javaVersion = "24";
          jdk = pkgs."jdk${javaVersion}";
          clojure = pkgs.clojure.override { inherit jdk; };
          libraries = [
            # Add any libraries needed for LD_LIBRARY_PATH here
          ];
        in
        {
          packages = [
            # Existing packages
            clojure
            # Build tools
            pkgs.gcc
            pkgs.gnumake
            pkgs.tup
            pkgs.jet
            # Language compilers and runtimes
            pkgs.nim
            pkgs.zig
            pkgs.go
            pkgs.rustc
            pkgs.cargo
            pkgs.dmd
            pkgs.ldc
            pkgs.ghc
            pkgs.ocaml
            pkgs.mono
            pkgs.nodejs
            pkgs.nodejs.pkgs.node-gyp
            pkgs.python3
            pkgs.python3Packages.matplotlib
            pkgs.python3Packages.numpy
            pkgs.dart
            pkgs.luajit
            pkgs.julia
            pkgs.elixir
            pkgs.erlang
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
            ln -sfn ${pkgs.jdk24} vendor/openjdk24 || true
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
