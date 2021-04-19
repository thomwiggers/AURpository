#!/bin/bash

set -e

rm -f /home/thom/.cache/aurutils/sync/shadow-tech/info.yml

dir=$(realpath "${BASH_SOURCE%/*}")
root=$(realpath "${BASH_SOURCE%/*}/packages")
$dir/aursync --pkgver --upgrade --ignore=ruby-kramdown-rfc2629 --ignore mongodb

mapfile -t packages < <($dir/vercmp-devel | cut -d: -f1)

if [ "${#packages[@]}" != "0" ]; then
    $dir/aursync --no-ver-argv "${packages[@]}"
else
    echo "All vcs packages up to date!"
fi

checkrebuild -i aurpkgs

echo -n "Currently packaged Shadow version:"
pacman -Si shadow-tech | grep Version | cut  -d: -f 2
echo -n "Latest shadow version: "
curl "https://storage.googleapis.com/shadow-update/launcher/prod/linux/ubuntu_18.04/latest-linux.yml" 2> /dev/null | yq '.version'
