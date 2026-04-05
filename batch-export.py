#!/usr/bin/env python3
"""
Export an SVG file to PNG at power-of-2 sizes (128, 256, 512, 1024).
Output files are saved to a `render/` subdirectory next to the SVG.

Requires resvg:
    pip install --user resvg-cli

Usage:
    py batch-export.py <path/to/file.svg>
"""

import sys
import subprocess
from pathlib import Path


SIZES = [128, 256, 512, 1024]


def find_resvg() -> list[str]:
    """Return the command to invoke resvg, or raise if not found."""
    # Try shell command first
    try:
        subprocess.run(["resvg", "--version"], capture_output=True, check=True)
        return ["resvg"]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Fall back to calling via the Python module (works even without PATH setup)
    try:
        import resvg_cli
        binary = Path(resvg_cli.__file__).parent / "resvg.exe"
        if not binary.exists():
            # Non-Windows
            binary = Path(resvg_cli.__file__).parent / "resvg"
        if binary.exists():
            return [str(binary)]
    except ImportError:
        pass

    raise FileNotFoundError(
        "resvg not found. Install it with:\n"
        "    pip install --user resvg-cli\n"
        "If already installed, try reinstalling with --user to fix permission issues."
    )


def export_png(resvg_cmd: list[str], svg_path: Path, size: int, output_dir: Path) -> Path:
    output_file = output_dir / f"{svg_path.stem}_{size}x{size}.png"
    result = subprocess.run(
        [*resvg_cmd, str(svg_path), str(output_file), "-w", str(size), "-h", str(size)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "resvg failed with no output")
    return output_file


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/file.svg>")
        sys.exit(1)

    svg_path = Path(sys.argv[1]).resolve()

    if not svg_path.exists():
        print(f"Error: file not found: {svg_path}")
        sys.exit(1)

    try:
        resvg_cmd = find_resvg()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_dir = svg_path.parent / "render"
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")

    for size in SIZES:
        try:
            out = export_png(resvg_cmd, svg_path, size, output_dir)
            print(f"  ✓ {size:>4}x{size:<4}  →  {out.name}")
        except Exception as e:
            print(f"  ✗ {size:>4}x{size:<4}  →  Error: {e}")
            sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()
