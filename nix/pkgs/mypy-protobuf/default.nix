{ lib
, python
, fetchFromGitHub
, buildPythonPackage
, stdenv
, six
, mypy
, protobuf
}:
let basename = "mypy-protobuf";
    buildInputs = with python.pkgs; [ six protobuf ];

mypyProtobuf = buildPythonApplication rec {
  name = "${basename}";
  version = "v1.13";

  src = fetchFromGitHub {
    owner  = "dropbox";
    repo   = "mypy-protobuf";
    rev    = "${version}";
    sha256 = "0fdv7xbl6fzjmng2lh192lj2inb3cp5v0276ri9klfpbrxb0p8cg";
  };

  format = "setuptools";

  nativeBuildInputs = buildInputs;
  propagatedBuildInputs = buildInputs;

  preBuild = ''
    pushd python
  '';
};

in mypyProtobuf
