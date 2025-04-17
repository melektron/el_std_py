# development shell for running test programs
let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.python312Packages.matplotlib
    pkgs.python312Packages.pydantic
    #(pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
    #  # select Python packages here
    #  numpy
    #  matplotlib
    #  pydantic
    #]))
  ];
  shellHook = ''
    source .venv/bin/activate
  '';
}