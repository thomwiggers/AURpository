#!/bin/bash

set -e
dir=$(realpath "${BASH_SOURCE%/*}")
root=$(realpath "${BASH_SOURCE%/*}/packages")
aur sync --database aurpkgs --root $root --sign --pkgver --upgrade

mapfile -t packages < <(aur vercmp-devel --database aurpkgs --root $root | cut -d: -f1)

if [ "${#packages[@]}" != "0" ]; then
    $dir/aursync "${packages[@]}" --no-ver-shallow
fi

rsync --delete --progress --copy-links --recursive $root/ archeron:/var/www/arch.rded.nl/
