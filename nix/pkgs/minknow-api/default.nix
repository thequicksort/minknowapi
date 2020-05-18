{ lib
, python
, fetchFromGitHub
, buildPythonPackage
, stdenv
, generateMypyStubs ? false # Whether to support mypy type stubs.
, mypy-protobuf ? null
}:
let basename = "minknow";
    buildInputs = with python.pkgs; [ protobuf grpcio grpcio-tools ]
    ++ lib.optional (generateMypyStubs) mypy-protobuf;

minknow = buildPythonPackage rec {
  name = "${basename}";
  version = "v3.6.0";

  src = fetchFromGitHub {
    owner  = "nanoporetech";
    repo   = "minknow_api";
    rev    = "${version}";
    sha256 = "12fbp8qjjbl9azl5cfq6aagx5298b0lq8lq0bi26rkdpa498j66q";
  };

  format = "other";

  nativeBuildInputs = buildInputs;
  propagatedBuildInputs = buildInputs;

  buildPhase = ''
    mkdir -p $TMPDIR/${basename}/generated/
    mkdir -p $TMPDIR/${basename}/mypy/
    ${python}/bin/python -m grpc_tools.protoc \''
    + lib.optionalString (generateMypyStubs) ''--plugin=protoc-gen-mypy=${mypy-protobuf.out}/bin/protoc-gen-mypy \''
    + lib.optionalString (generateMypyStubs) ''--mypy_out=$TMPDIR/${basename}/generated \''
    +
    ''
      --python_out=$TMPDIR/${basename}/generated/ \
      --grpc_python_out=$TMPDIR/${basename}/generated/ \
      -I $src/. $src/minknow/rpc/*.proto
  ''
  ;

  installPhase = ''
    mkdir -p "$out/${python.sitePackages}"
    cp -r $TMPDIR/${basename}/generated/** "$out/${python.sitePackages}/"
  ''
  #+
  #lib.optionalString (generateMypyStubs) ''cp -r $TMPDIR/${basename}/mypy/** "$out/${python.sitePackages}/"''
  +
  ''
    export PYTHONPATH="$out/${python.sitePackages}:$PYTHONPATH"
  '';

};

in minknow
