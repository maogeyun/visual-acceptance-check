# 视觉验收示例

基于 ChatBI 首页设计稿 vs 开发实现的对照验收（节选，仅视觉要素）。

## 输入（MasterGo + 开发截图）

- 设计基准：MasterGo 链接 `https://{domain}/file/{fileId}?layer_id={layerId}` → `mcp__getDsl` → `design-baseline.json`（帧 1920×960）
- 开发截图：用户本机登录后截取 1920×960 PNG
- 视口：与 MasterGo 帧一致

## 差异实例（findings）

```yaml
- id: F-001
  checkpoint_code: VA-COLOR-GRADIENT
  label: 1
  severity: general
  deduction: 1
  region: "主标题 ChatBI"
  bbox_px: [547, 198, 115, 36]
  design: "linear-gradient(180deg, #fc6506, #fc8506)"
  actual: "color: #ff7a00"
  fix: "应用 --gradient-brand-text"
  verified_by: screenshot

- id: F-002
  checkpoint_code: VA-FONT-SIZE
  label: 2
  severity: general
  deduction: 1
  region: "欢迎标题"
  bbox_px: [403, 162, 504, 54]
  design: "32px Medium #333"
  actual: "28px #333"
  verified_by: screenshot

- id: F-003
  checkpoint_code: VA-SPACING-BOX
  label: 3
  region: "卡片组 gap"
  bbox_px: [360, 315, 720, 225]
  design: "gap: 31px"
  actual: "gap: 16px"
  verified_by: screenshot

- id: F-004
  checkpoint_code: VA-LAYOUT-MISSING
  label: 4
  severity: major
  deduction: 2
  region: "数据主题切换"
  bbox_px: [360, 558, 720, 36]
  design: "数据主题切换胶囊行"
  actual: "完全缺失"
  verified_by: screenshot

- id: F-005
  checkpoint_code: VA-RADIUS
  label: 5
  region: "卡片左上"
  bbox_px: [360, 315, 230, 180]
  design: "border-radius: 6px"
  actual: "border-radius: 8px"
  verified_by: screenshot
```

## 扣分明细（checkpoint_ledger 节选）

| checkpoint_code | 检查点 | 检测 | 通过 | 不通过 | 原始 | 调整 | 合计 | 状态 | finding_ids |
|-----------------|--------|------|------|--------|------|------|------|------|-------------|
| VA-COLOR-GRADIENT | 颜色-渐变 | 1 | 0 | 1 | −1 | 0 | −1 | fail | F-001 |
| VA-FONT-SIZE | 字体-字号 | 1 | 0 | 1 | −1 | 0 | −1 | fail | F-002 |
| VA-SPACING-BOX | 间距-Gap | 1 | 0 | 1 | −1 | 0 | −1 | fail | F-003 |
| VA-LAYOUT-MISSING | 模块缺失 | 1 | 0 | 1 | −2 | 0 | −2 | fail | F-004 |
| VA-RADIUS | 圆角 | 3 | 2 | 1 | −1 | 0 | −1 | fail | F-005 |
| VA-COLOR-HEX | 颜色-HEX | 0 | 0 | 0 | 0 | 0 | 0 | untested | — |
| VA-FONT-WEIGHT | 字体-字重 | 12 | 12 | 0 | 0 | 0 | 0 | pass | — |

完整报告须列出编码表**全部 24 个 VA-* 检查点**（其余为 pass / untested / na）。

## 计分演算

**合计扣分**：−6 → **视觉得分 94** → **达标**

## HTML 精准标注报告

报告首屏为**全宽开发截图 + SVG 标注层**：
- 5 条 findings → 截图上 **5 个编号框**（label 1–5），框线贴元素边界
- 点击差异表行 / 底部图例 → 高亮对应标注
- 「聚焦模式」淡化其余框；「显示说明标签」在框旁显示区域名

```bash
python3 ~/.cursor/skills/visual-acceptance-check/scripts/bake-annotations.py \
  dev-screenshot.png findings.json -o annotated.png
```

## HTML 数据结构示例

```json
{
  "image_size": { "width": 1440, "height": 900 },
  "scores": { "total": 94, "grade": "达标" },
  "findings": [
    {
      "id": "F-001", "label": 1, "checkpoint_code": "VA-COLOR-GRADIENT",
      "region": "主标题 ChatBI", "severity": "general", "deduction": 1,
      "design": "linear-gradient #fc6506→#fc8506", "actual": "纯色 #ff7a00",
      "fix": "使用 --gradient-brand-text",
      "bbox_px": [547, 198, 115, 36]
    }
  ]
}
```
