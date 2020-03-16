#!/bin/bash

set -e

dir=$(realpath "${BASH_SOURCE%/*}")
root=$(realpath "${BASH_SOURCE%/*}/packages")
$dir/aursync --pkgver --upgrade

mapfile -t packages < <($dir/vercmp-devel | cut -d: -f1)

if [ "${#packages[@]}" != "0" ]; then
    $dir/aursync --no-ver-argv "${packages[@]}"
else
    echo "All vcs packages up to date!"
fi

#rsync --delete --progress --copy-links --recursive $root/ archeron.rded.nl:/var/www/arch.rded.nl/
