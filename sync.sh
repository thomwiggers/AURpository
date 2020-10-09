#!/bin/bash

set -e

rm -f /home/thom/.cache/aurutils/sync/shadow-tech/info.yml

dir=$(realpath "${BASH_SOURCE%/*}")
root=$(realpath "${BASH_SOURCE%/*}/packages")
$dir/aursync --pkgver --upgrade

mapfile -t packages < <($dir/vercmp-devel | cut -d: -f1)

if [ "${#packages[@]}" != "0" ]; then
    $dir/aursync --no-ver-argv "${packages[@]}"
else
    echo "All vcs packages up to date!"
fi

