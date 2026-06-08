"""视觉验收脚本共享工具（纯函数，便于单测）。"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any

REPORT_DATA_PLACEHOLDER = "__VA_REPORT_DATA__"
EMBED_THRESHOLD_BYTES = 5 * 1024 * 1024  # 5MB

GRADE_CLASSES = {
    "优秀": "grade-excellent",
    "达标": "grade-pass",
    "有条件通过": "grade-conditional",
}


def resolve_path(base_dir: Path, path: Path) -> Path:
    return path if path.is_absolute() else base_dir / path


def b64_file(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _relative_image_src(image_path: Path, html_output: Path) -> str:
    rel = os.path.relpath(image_path.resolve(), html_output.parent.resolve())
    return rel.replace("\\", "/")


def image_embed_fields(
    image_path: Path,
    html_output: Path,
    *,
    base64_key: str,
    src_key: str,
    threshold: int = EMBED_THRESHOLD_BYTES,
) -> dict[str, str]:
    """大图用相对路径，小图内嵌 base64。"""
    size = image_path.stat().st_size
    if size <= threshold:
        return {base64_key: b64_file(image_path)}

    rel = _relative_image_src(image_path, html_output)
    return {src_key: rel}


def safe_json_for_script_tag(data: dict[str, Any]) -> str:
    """Serialize JSON safe to embed inside <script> (escape </script>)."""
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if "</script>" in payload.lower() or "</" in payload:
        payload = payload.replace("<", "\\u003c")
    return payload


def infer_viewport_mode(width: int, meta: str) -> str:
    if width <= 500:
        return "mobile"
    if re.search(r"\b375\b|\bH5\b|\bmobile\b", meta, re.I):
        return "mobile"
    return "desktop"


def grade_from_total(total: int) -> str:
    if total >= 95:
        return "优秀"
    if total >= 85:
        return "达标"
    if total >= 70:
        return "有条件通过"
    return "不通过"


def parse_image_size(scores: dict[str, Any]) -> tuple[int, int]:
    raw_size = scores.get("image_size")
    if isinstance(raw_size, dict):
        return int(raw_size.get("width") or 0), int(raw_size.get("height") or 0)
    if isinstance(raw_size, list) and len(raw_size) == 2:
        return int(raw_size[0]), int(raw_size[1])
    return 0, 0


def resolve_bbox(finding: dict[str, Any], img_w: int, img_h: int) -> list[int] | None:
    bbox_px = finding.get("bbox_px")
    if isinstance(bbox_px, list) and len(bbox_px) == 4:
        return [int(v) for v in bbox_px]

    bbox = finding.get("bbox")
    if isinstance(bbox, list) and len(bbox) == 4:
        x, y, w, h = bbox
        return [
            round(x / 100 * img_w),
            round(y / 100 * img_h),
            round(w / 100 * img_w),
            round(h / 100 * img_h),
        ]
    return None


def inject_report_data(template: str, data: dict[str, Any]) -> str:
    payload = safe_json_for_script_tag(data)
    if REPORT_DATA_PLACEHOLDER not in template:
        raise ValueError(f"模板缺少占位符 {REPORT_DATA_PLACEHOLDER}")
    return template.replace(REPORT_DATA_PLACEHOLDER, payload, 1)
