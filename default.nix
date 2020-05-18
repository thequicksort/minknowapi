###########################################################################################
#
# default.nix
#
###########################################################################################
#
# This expression builds the Poretitioner application.
#   - To see how this application is built, see the `App` section.
#       Build with "nix-build -A app"
#       To build without testing (only recommended for local builds and rapid-prototyping)
#   - To see how this application is packaged for Docker, see the `Docker` section.
#
###########################################################################################

{ pkgs ? import <nixpkgs> { config = (import ./nix/config.nix); }
, cudaSupport ? false
, python ? (pkgs.callPackage ./nix/python.nix) { inherit pkgs; }
}:

with pkgs;
let
  # REPLACE WITH YOUR PROJECT NAME
  name = "minknow";
  # REPLACE WITH YOUR VERSION
  version = "0.1.0";

  ############################################################
  #
  # App - Builds the actual poretitioner application.
  #
  ############################################################
  dependencies = callPackage ./nix/dependencies.nix { inherit python cudaSupport; };
  run_pkgs = dependencies.run;
  test_pkgs = dependencies.test;
in
  # doCheck - Whether to run the test suite as part of the build, defaults to true.
  # To understand how `buildPythonApplication` works, check out https://github.com/NixOS/nixpkgs/blob/master/pkgs/development/interpreters/python/mk-python-derivation.nix
  python.pkgs.buildPythonPackage {
    pname = name;
    version = version;

    src = ./.;

    checkInputs = test_pkgs;
    doCheck = false;
    checkPhase = "pytest tests";

    # Run-time dependencies
    propagatedBuildInputs = run_pkgs;
}