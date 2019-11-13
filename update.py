#!/usr/bin/env python3.8
from typing import Optional, Literal, List

import os
import glob
import shlex
import shutil
import subprocess


def getyesno(prompt: str, default: Optional[Literal['y', 'n']] = None) -> bool:
    options = "Y" if default == 'y' else 'y'
    options += "N" if default == 'n' else 'n'
    while True:
        result = input(f"{prompt} [{options}]: ").strip().lower()
        if default is not None and result == '':
            return default == 'y'
        elif result == 'y':
            return True
        elif result == 'n':
            return False
        continue


def move(src, dest):
    filename = os.path.basename(src)
    if os.path.exists(os.path.join(dest, filename)):
        os.remove(os.path.join(dest, filename))
    shutil.move(src, dest)


def run(command: str,
        capture_output: bool = True,
        check: bool = True,
        cwd: Optional[str] = None) -> (
        subprocess.CompletedProcess):

    try:
        return subprocess.run(
            shlex.split(command),
            text=True,
            capture_output=capture_output,
            check=True,
            cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Stdout = {e.stdout}")
        print(f"Stderr = {e.stderr}")
        raise e


def clone_repo(package: str) -> None:
    repodir = os.path.join('repos', package)
    if os.path.exists(repodir):
        print(f"{package} already cloned")
        return
    run(f"git clone https://aur.archlinux.org/{package}.git",
        cwd='repos')
    print(f"Cloned {package}")
    for filename in glob.glob(os.path.join(repodir, '*')):
        run(f"diff --unified  /dev/null {filename}",
            check=False,
            capture_output=False)
    assert getyesno("Accept this package?")


def needs_update(package: str) -> bool:
    if "-git" in package:
        return True
    count = len(glob.glob(os.path.join('packages', f"{package}-*.pkg.tar.xz")))
    if count == 0:
        return True
    path = os.path.join('repos', package)
    run("git fetch", cwd=path)
    if 'up to date' in run("git status", cwd=path).stdout:
        return False

    # Generate diff
    run("git diff master origin/master",
        capture_output=False, check=False, cwd=path)
    assert getyesno("Diff approved?")
    run("git reset --hard origin/master", cwd=path)
    return True


def build_package(package: str) -> List[str]:
    path = os.path.join('repos', package)
    run("makepkg --force --syncdeps --check --sign",
        capture_output=False,
        cwd=path)
    pkgs = glob.glob(os.path.join("repos", package, f"{package}-*.pkg.tar.xz"))
    sigs = glob.glob(os.path.join("repos", package,
                                  f"{package}-*.pkg.tar.xz.sig"))
    filenames = []
    for pkg in pkgs:
        filenames.append(os.path.basename(pkg))
        move(pkg, "packages")
    for sig in sigs:
        move(sig, "packages")
    return filenames


def add_to_repo(package: str) -> None:
    print(f"Adding {package} to repository db")
    run("repo-add --sign --prevent-downgrade --remove --new "
        f"{os.path.join('packages', 'aurpkgs.db.tar.gz')} "
        f"{os.path.join('packages', package)}")


def sync_to_server() -> None:
    run("rsync --delete --progress --copy-links --recursive packages/ "
        "archeron:/var/www/arch.rded.nl/",
        capture_output=False)


def main():
    with open('packages.txt', 'r') as f:
        packages = map(str.strip, f.readlines())
    for package in packages:
        print(f"Processing {package}")
        clone_repo(package)
        build = needs_update(package)
        if build:
            new_packages = build_package(package)
            for pkg in new_packages:
                add_to_repo(pkg)

    sync_to_server()


if __name__ == "__main__":
    main()
