#!/usr/bin/env python3
"""从验收产物目录生成 HTML 报告。

用法:
  python3 generate-report.py --dir reports/visual-acceptance-xxx \\
    --title "首页视觉验收" --meta "375×812 · H5 · 2026-05-26" \\
    --dev dev.png --baseline design-baseline.json \\
    --findings findings.json --ledger checkpoint-ledger.json \\
    --scores scores.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from va_utils import (
    GRADE_CLASSES,
    grade_from_total,
    image_embed_fields,
    infer_viewport_mode,
    inject_report_data,
    parse_image_size,
    resolve_path,
)


def load_json(path: Path) -> Any:
    if not path.exists():
        print(f"JSON 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def read_image_size(dev_path: Path, frame: dict[str, Any]) -> tuple[int, int]:
    try:
        from PIL import Image

        with Image.open(dev_path) as im:
            return im.size
    except ImportError:
        print("未安装 Pillow，使用 baseline 帧尺寸作为 image_size", file=sys.stderr)
    except OSError as exc:
        print(f"无法读取截图尺寸 ({dev_path}): {exc}", file=sys.stderr)

    fw = frame.get("width") or 1440
    fh = frame.get("height") or 900
    return int(fw), int(fh)


def build_scores_from_ledger(report_dir: Path, scores_path: Path) -> Path:
    findings = load_json(report_dir / "findings.json")
    ledger = load_json(report_dir / "checkpoint-ledger.json")
    deduction = sum(c.get("final_deduction") or 0 for c in ledger)
    total = max(0, 100 - deduction)
    meta_path = report_dir / "report-meta.json"
    meta = load_json(meta_path) if meta_path.exists() else {}
    img = meta.get("image") or [1125, 5298]
    scores = {
        "total": total,
        "grade": grade_from_total(total),
        "deduction": deduction,
        "findingsCount": len(findings),
        "image_size": img,
    }
    with scores_path.open("w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    return scores_path


def build_report_data(args: argparse.Namespace, html_output: Path) -> dict[str, Any]:
    dev_path = resolve_path(args.dir, args.dev)
    if not dev_path.exists():
        print(f"开发截图不存在: {dev_path}", file=sys.stderr)
        sys.exit(1)

    baseline = load_json(resolve_path(args.dir, args.baseline))
    findings = load_json(resolve_path(args.dir, args.findings))
    ledger = load_json(resolve_path(args.dir, args.ledger))
    scores = load_json(resolve_path(args.dir, args.scores))

    frame = baseline.get("frame") or {}
    img_w, img_h = parse_image_size(scores)
    if not img_w or not img_h:
        img_w, img_h = read_image_size(dev_path, frame)

    design_link = frame.get("source") or baseline.get("designLink") or ""
    design_frame = {
        "name": frame.get("name") or "设计帧",
        "width": frame.get("width"),
        "height": frame.get("height"),
    }

    meta_path = args.dir / "report-meta.json"
    actions: dict[str, list[str]] = {"must": [], "should": [], "later": []}
    untested: list[str] = []
    if meta_path.exists():
        meta_obj = load_json(meta_path)
        actions = meta_obj.get("actions") or actions
        untested = meta_obj.get("untested") or []

    grade = scores.get("grade", "—")
    grade_class = scores.get("gradeClass") or GRADE_CLASSES.get(grade, "grade-fail")
    viewport_mode = scores.get("viewportMode") or infer_viewport_mode(img_w, args.meta)

    report: dict[str, Any] = {
        "title": args.title,
        "meta": args.meta,
        "scores": {
            "total": scores.get("total"),
            "grade": grade,
            "deduction": scores.get("deduction", 0),
            "findingsCount": scores.get("findingsCount", len(findings)),
        },
        "gradeClass": grade_class,
        "designLink": design_link,
        "designFrame": design_frame,
        "image_size": {"width": img_w, "height": img_h},
        "viewportMode": viewport_mode,
        "displayHint": scores.get("displayHint")
        or (
            "H5 全页截图：标注区默认限制高度，可滚动或展开全页查看"
            if viewport_mode == "mobile"
            else ""
        ),
        "checkpointLedger": ledger,
        "findings": findings,
        "actions": actions,
        "untested": untested,
    }

    report.update(
        image_embed_fields(
            dev_path,
            html_output,
            base64_key="actualImageBase64",
            src_key="actualImageSrc",
            threshold=args.embed_threshold,
        )
    )

    if args.design:
        design_path = resolve_path(args.dir, args.design)
        if design_path.exists():
            report.update(
                image_embed_fields(
                    design_path,
                    html_output,
                    base64_key="designImageBase64",
                    src_key="designImageSrc",
                    threshold=args.embed_threshold,
                )
            )

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate visual acceptance HTML report")
    parser.add_argument("--dir", type=Path, required=True, help="Report output directory")
    parser.add_argument("--title", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--dev", type=Path, default=Path("dev.png"))
    parser.add_argument("--design", type=Path, default=None, help="Optional design PNG")
    parser.add_argument("--baseline", type=Path, default=Path("design-baseline.json"))
    parser.add_argument("--findings", type=Path, default=Path("findings.json"))
    parser.add_argument("--ledger", type=Path, default=Path("checkpoint-ledger.json"))
    parser.add_argument("--scores", type=Path, default=Path("scores.json"))
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output HTML path (default: <dir>/visual-acceptance-report.html)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "report-template.html",
    )
    parser.add_argument(
        "--embed-threshold",
        type=int,
        default=5 * 1024 * 1024,
        help="Images larger than this (bytes) use relative path instead of base64 (default: 5MB)",
    )
    args = parser.parse_args()

    scores_path = resolve_path(args.dir, args.scores)
    if not scores_path.exists():
        scores_path = build_scores_from_ledger(args.dir, scores_path)
    args.scores = scores_path

    if not args.template.exists():
        print(f"模板不存在: {args.template}", file=sys.stderr)
        sys.exit(1)

    out = args.output or args.dir / "visual-acceptance-report.html"
    data = build_report_data(args, out)
    template = args.template.read_text(encoding="utf-8")

    try:
        html = inject_report_data(template, data)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    if data.get("actualImageSrc"):
        print(f"Wrote {out}（开发截图 {data['actualImageSrc']} 外链，未内嵌 base64）")
    else:
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
