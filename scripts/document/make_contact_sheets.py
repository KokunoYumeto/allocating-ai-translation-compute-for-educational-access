#!/usr/bin/env python3
"""Create labeled contact sheets from render_docx.py page PNGs for visual QA."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def page_number(path: Path) -> int:
    match = re.search(r"(\d+)$", path.stem)
    return int(match.group(1)) if match else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--per-sheet", type=int, default=6)
    parser.add_argument("--cell-width", type=int, default=560)
    parser.add_argument("--cell-height", type=int, default=735)
    args = parser.parse_args()
    pages = sorted(args.render_dir.glob("page-*.png"), key=page_number)
    if not pages:
        raise SystemExit("No page PNGs found")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    columns = 2
    rows = math.ceil(args.per_sheet / columns)
    cell_w, cell_h, label_h, gap = args.cell_width, args.cell_height, 30, 18
    font = ImageFont.load_default()
    for sheet_index in range(0, len(pages), args.per_sheet):
        batch = pages[sheet_index : sheet_index + args.per_sheet]
        canvas = Image.new("RGB", (columns * cell_w + (columns + 1) * gap, rows * cell_h + (rows + 1) * gap), "#D7DCE2")
        draw = ImageDraw.Draw(canvas)
        for offset, path in enumerate(batch):
            with Image.open(path) as source:
                page = source.convert("RGB")
                page.thumbnail((cell_w - 2 * gap, cell_h - label_h - 2 * gap), Image.Resampling.LANCZOS)
            col, row = offset % columns, offset // columns
            x = gap + col * (cell_w + gap)
            y = gap + row * (cell_h + gap)
            draw.text((x + 4, y + 4), f"Page {page_number(path)}", fill="#16283A", font=font)
            px = x + (cell_w - page.width) // 2
            py = y + label_h
            canvas.paste(page, (px, py))
            draw.rectangle((px - 1, py - 1, px + page.width, py + page.height), outline="#7B8794", width=1)
        first, last = page_number(batch[0]), page_number(batch[-1])
        output = args.output_dir / f"contact_{first:03d}_{last:03d}.png"
        canvas.save(output, optimize=True)
    print(f"pages={len(pages)} sheets={math.ceil(len(pages) / args.per_sheet)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
