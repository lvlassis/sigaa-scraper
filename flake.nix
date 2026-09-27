{
  description = "Scraper do portal discente do SIGAA UFG";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        version = "0.3.0";

        sigaa-scraper = pkgs.python312Packages.buildPythonApplication {
          pname = "sigaa-scraper";
          inherit version;
          pyproject = true;

          src = ./.;

          build-system = with pkgs.python312Packages; [
            hatchling
            hatch-vcs
          ];

          dependencies = with pkgs.python312Packages; [
            requests
            parsel
          ];

          # hatch-vcs tenta ler a versão via git, o que não funciona em
          # build puro do Nix — esta variável injeta a versão diretamente.
          preBuild = ''
            export SETUPTOOLS_SCM_PRETEND_VERSION=${version}
          '';

          meta = with pkgs.lib; {
            description = "Scraper do portal discente do SIGAA UFG";
            homepage = "https://github.com/lvlassis/sigaa-scraper";
            license = licenses.mit;
            mainProgram = "sigaa-scraper";
          };
        };
      in
      {
        packages.default = sigaa-scraper;

        devShells.default = pkgs.mkShell {
          packages = [ pkgs.uv pkgs.python312 ];
        };
      }
    );
}
