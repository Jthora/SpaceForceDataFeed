{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.glibcLocales
  ];
}
