let
  pkgs = import <nixpkgs> { };
  stdenv = pkgs.stdenv;
  defaultPython = pkgs.python37;
in { python ? defaultPython, generateMypyStubs ? true }: with python.pkgs; callPackage ./default.nix { inherit python generateMypyStubs; }
