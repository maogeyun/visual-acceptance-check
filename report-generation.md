# 报告生成规范

解决两类常见问题：**H5 长截图占屏过大**、**仅 MasterGo 链接无预览图时设计侧显示错误**。

## 数据字段（REPORT_DATA）

| 字段 | 必填 | 说明 |
|------|------|------|
| `actualImageBase64` | 二选一 | 开发截图 base64（≤5MB 时默认内嵌） |
| `actualImageSrc` | 二选一 | 大图外链相对路径，如 `dev.png`（与 HTML 同目录） |
| `image_size` | 是 | `{ width, height }` 与截图像素一致 |
| `designLink` | 有链接时 | MasterGo `frame.source` 或用户设计稿 URL |
| `designFrame` | 推荐 | `{ name, width, height }` 来自 `design-baseline.json` |
| `designImageBase64` | 可选 | 设计稿 PNG base64 |
| `designImageSrc` | 可选 | 设计稿外链相对路径（大图时） |
| `viewportMode` | 推荐 | `"mobile"`（宽 ≤500）或 `"desktop"` |
| `displayHint` | 可选 | 如 `"H5 全页截图，默认视口高度内滚动查看"` |

## 设计稿侧展示规则

优先级：

1. **有 `designImageBase64` 或 `designImageSrc`** → 显示预览图  
2. **仅有 `designLink`** → 显示可点击链接卡片 + 帧名/尺寸；**隐藏 `<img>`，禁止空 src**  
3. 两者皆无 → 显示「未提供设计预览」说明

从 `design-baseline.json` 读取：

```json
"designLink": "https://mastergo.com/goto/...",
"designFrame": { "name": "首页", "width": 375, "height": 1962 }
```

## H5 / 长页截图展示规则

**禁止**将全页 H5 截图以容器 100% 宽度直接铺开（阅读高度可达数千像素）。

模板默认行为（`report-template.html`）：

| 模式 | 条件 | 表现 |
|------|------|------|
| 移动端框 | `viewportMode: mobile` 或 `image_size.width ≤ 500` | 截图最大宽 **375px** 居中 |
| 滚动视口 | 高宽比 > 2 或高度 > 1200px | 标注区 **max-height: min(70vh, 720px)** 内滚动 |
| 展开全页 | 用户点击工具栏 | 取消高度限制 |

生成报告时：

- `bbox_px` 仍相对**全页截图**坐标；滚动容器内 SVG 标注与图片同步滚动  
- 可选额外导出 `dev-viewport.png`（首屏）供快速浏览，但 HTML 标注须用全页图

## 推荐命令

```bash
SKILL=~/.cursor/skills/visual-acceptance-check
OUT=reports/visual-acceptance-<page>-<timestamp>

python3 "$SKILL/scripts/generate-report.py" \
  --dir "$OUT" \
  --title "首页视觉验收" \
  --meta "375×812 · H5 · 2026-05-26" \
  --dev dev.png \
  --baseline design-baseline.json \
  --findings findings.json \
  --ledger checkpoint-ledger.json \
  --scores scores.json
```

`scores.json` 示例：

```json
{ "total": 98, "grade": "优秀", "deduction": 2, "findingsCount": 2 }
```

## 开验后检查

- [ ] 设计侧：有链接则可见可点，无破图图标  
- [ ] 开发侧：首屏在 70vh 内可见，可滚动查看全页  
- [ ] 移动端截图宽度约 375px，非整页 1280px 拉宽  
- [ ] 点击差异行可滚动到对应标注位置  
