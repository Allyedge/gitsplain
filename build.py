#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
from pathlib import Path


def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def build_binary():
    system = platform.system().lower()

    if system == "windows":
        binary_name = "gitsplain.exe"
    else:
        binary_name = "gitsplain"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", binary_name,
        "--clean",
        "src/main.py"
    ]

    run_command(cmd)

    dist_dir = Path("dist")
    binary_path = dist_dir / binary_name

    if not binary_path.exists():
        print(f"Error: Built binary not found at {binary_path}", file=sys.stderr)
        sys.exit(1)

    print(f"\nBuild successful! Binary located at: {binary_path}")
    print(f"Size: {binary_path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    build_binary()
