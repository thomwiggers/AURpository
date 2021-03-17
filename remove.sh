repo-remove --sign packages/aurpkgs.db.tar.gz $@

echo "Don't forget to remove the binaries"

for arg in $@; do
    ls packages/$arg
done
