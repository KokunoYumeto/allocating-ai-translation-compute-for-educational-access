#!/usr/bin/env python3
"""Build numbered 2x2 contact sheets from render_docx page PNGs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def page_number(path: Path) -> int:
    match = re.fullmatch(r"page-(\d+)\.png", path.name)
    if not match:
        raise ValueError(path.name)
    return int(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--thumb-width", type=int, default=900)
    args = parser.parse_args()

    pages = sorted(args.input_dir.glob("page-*.png"), key=page_number)
    if not pages:
        raise SystemExit("no page PNGs found")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()

    for start in range(0, len(pages), 4):
        batch = pages[start : start + 4]
        rendered: list[tuple[int, Image.Image]] = []
        for path in batch:
            with Image.open(path) as original:
                image = original.convert("RGB")
            height = round(image.height * args.thumb_width / image.width)
            rendered.append((page_number(path), image.resize((args.thumb_width, height), Image.Resampling.LANCZOS)))
        cell_height = max(image.height for _, image in rendered) + 36
        sheet = Image.new("RGB", (args.thumb_width * 2, cell_height * 2), "white")
        draw = ImageDraw.Draw(sheet)
        for index, (number, image) in enumerate(rendered):
            x = (index % 2) * args.thumb_width
            y = (index // 2) * cell_height
            draw.text((8 + x, 8 + y), f"page-{number}", fill="black", font=font)
            sheet.paste(image, (x, y + 28))
        first = page_number(batch[0])
        last = page_number(batch[-1])
        sheet.save(args.output_dir / f"pages_{first:02d}_{last:02d}.jpg", quality=90, optimize=True)

    print(f"pages={len(pages)} sheets={(len(pages) + 3) // 4}")


if __name__ == "__main__":
    main()
