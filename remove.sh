#!/bin/zsh

for pkg in $@; do
    pkg="$(echo $(basename ${pkg}) | perl -pe 's/^(.*?)-([^-]+)(-\d+)?-(any|x86_64)\.pkg\..*$/$1/')"
    if (($pkgs[(Ie)$pkg])); then
        echo "duplicate $pkg"
        continue
    fi
    pkgs=($pkgs $pkg)
    repo-remove --sign packages/aurpkgs.db.tar.gz ${pkg}
    rm -fi packages/$pkg-*.pkg.*
done
