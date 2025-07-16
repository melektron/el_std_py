{
  description = "el_std_py";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: 
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        # build of python package for flake consumption
        packages.default = pkgs.python313Packages.buildPythonPackage
        {
          pname = "el-std-py";
          version = "0.3.0";
          pyproject = true;

          src = ./.;

          build-system = [
            pkgs.python313Packages.setuptools
          ];
        };

        # shell with some optional libraries for development
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python313Packages.matplotlib
            pkgs.python313Packages.pydantic
            pkgs.python313Packages.tkinter
            pkgs.python313Packages.customtkinter
            pkgs.python313Packages.numpy
            pkgs.python313Packages.pytest
            pkgs.python313Packages.pytest-asyncio
          ];
          shellHook = ''
            #source .venv/bin/activate
          '';
        };
      }
    );
}
