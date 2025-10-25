#!/bin/python3

import os
import sys

CUR_DIR: str = os.path.abspath(os.path.dirname(__file__))
DST_DIR = os.path.realpath(os.path.expandvars("$HOME"))
BAK_DIR: str = os.path.join(CUR_DIR, ".BAK")


def _get_src_files(root: str) -> list[str]:
    src_files: list[str] = []
    for src in os.listdir(os.path.join(root, "_config")):
        src_files.append(os.path.join("_config", src))
    for src in os.listdir(os.path.join(root, "_local", "share")):
        src_files.append(os.path.join("_local", "share", src))
    return src_files


def _dot(src, dst):
    dst_exist = os.path.exists(dst) or os.path.islink(dst)
    bak = BAK_DIR
    if dst_exist:
        print("dst={0:<60} bak={1}".format(dst, bak), file=sys.stderr)
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.move(dst, bak)
    os.symlink(src, dst)


def main():
    src_files = _get_src_files(CUR_DIR)
    for src_file in src_files:
        _dot(os.path.join(CUR_DIR, src_file), os.path.join(DST_DIR, "." + src_file[1:]))
    print(src_files)
    pass


if __name__ == "__main__":
    main()
