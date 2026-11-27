#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 v3 entry (make.fun harness).

Standard library only. The image is drawn by build_image.py and
committed as entry.png; this program just copies it to
MAKEFUN_OUTPUT_DIR (default /output), so two runs write byte-identical
output.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(here, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
