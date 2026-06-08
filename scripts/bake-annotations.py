#!/usr/bin/env python3
"""将 findings 的 bbox 烘焙到开发截图上，输出带编号标注的 PNG。

用法:
  python3 bake-annotations.py screenshot.png findings.json -o annotated.png

findings.json 格式:
  [{ "label": 1, "severity": "general", "region": "...", "bbox_px": [x,y,w,h] }]
  或含 "bbox": [x%,y%,w%,h%]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要 Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)

SEVERITY_COLOR = {
    "general": (245, 158, 11),
    "major": (239, 68, 68),
    "fatal": (127, 29, 29),
}

FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/msyh.ttc",
)


def load_font(size: int = 14) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


from va_utils import resolve_bbox


def draw_label(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    x: int,
    y: int,
    label: str,
    color: tuple[int, int, int],
) -> None:
    text = str(label)
    radius = max(12, len(text) * 6 + 6)
    lx = max(0, x - radius // 4)
    ly = max(0, y - radius // 4)
    draw.ellipse([lx, ly, lx + radius, ly + radius], fill=color + (255,))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (lx + (radius - tw) / 2, ly + (radius - th) / 2 - 1),
        text,
        fill=(255, 255, 255, 255),
        font=font,
    )


def bake_annotations(
    image_path: Path,
    findings: list[dict[str, Any]],
    output_path: Path,
) -> int:
    drawn = 0
    font = load_font()

    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        w, h = img.size

        for finding in findings:
            box = resolve_bbox(finding, w, h)
            if not box:
                fid = finding.get("id", finding.get("label"))
                print(f"跳过无 bbox: {fid}", file=sys.stderr)
                continue

            x, y, bw, bh = box
            severity = finding.get("severity", "general")
            color = SEVERITY_COLOR.get(severity, SEVERITY_COLOR["general"])
            width = 3 if severity == "fatal" else 2
            draw.rectangle([x, y, x + bw, y + bh], outline=color + (255,), width=width)
            draw_label(draw, font, x, y, finding.get("label", ""), color)
            drawn += 1

        out = Image.alpha_composite(img, overlay).convert("RGB")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.save(output_path, "PNG")

    return drawn


def main() -> None:
    parser = argparse.ArgumentParser(description="Bake finding annotations onto screenshot")
    parser.add_argument("image", type=Path)
    parser.add_argument("findings", type=Path, help="JSON array of findings")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    if not args.image.exists():
        print(f"截图不存在: {args.image}", file=sys.stderr)
        sys.exit(1)
    if not args.findings.exists():
        print(f"findings 不存在: {args.findings}", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(args.findings.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        print("findings.json 必须是数组", file=sys.stderr)
        sys.exit(1)

    drawn = bake_annotations(args.image, raw, args.output)
    print(f"已写入 {args.output}（{drawn}/{len(raw)} 条标注）")


if __name__ == "__main__":
    main()
