# 全量 24 检查点走查清单

目标：**每个 VA-* 必须有 `pass` / `fail` / `na`**，禁止批量 `untested`。

## 三层验收

| 层 | 输入 | 产出 |
|----|------|------|
| **L1 宏观** | MasterGo 帧结构 + 开发截图 | 模块缺失、栅格列数、图标语义 |
| **L2 Token** | `design-baseline.json` + 截图抽样 / 肉眼 | 颜色/字体的可见偏差 |
| **L3 运行时** | 开发 URL + CDP（可选） | 间距/圆角/阴影精确 px |

**防误判**：L1/L3 路由、采图、DSL 文案、CDP 取样规则见 [acceptance-guardrails.md](acceptance-guardrails.md)。

**MasterGo 链接 + 开发截图**（无 URL）时：L1 + L2 必做；L3 列入待补测。

## 分区抽样（每页 3–8 区）

对每区每类至少 **1 个锚点**；全页每 VA-* 子类合计 **≥3 个样本** 方可标 `pass`。

| 区域示例 | 颜色 | 字体 | 间距 | 圆角/阴影 | 图标 |
|----------|------|------|------|-----------|------|
| 顶栏 | 链接色、Logo 色 | 菜单字号 | 菜单 gap | — | 工具栏图标 |
| 页签 | 激活态色 | Tab 字 | Tab padding | Tab 圆角 | 关闭 × |
| 主表格 | 状态色、链接色 | 表头/正文 | 行高、cell padding | 卡片 shadow | — |
| 侧栏卡片 | 强调色 | 标题/副文 | 卡片 padding | 卡片 radius | 功能图标 |
| 列表/空态 | 次要文字色 | 空态文案 | item gap | — | 空态插图 |

## 逐检查点执行表

| checkpoint_code | L1 | L2 MasterGo baseline | L3 CDP | na 条件 |
|-----------------|----|----------------------|--------|---------|
| VA-COLOR-HEX | — | 抽样 3 处 hex 对比 | `color`/`backgroundColor` | — |
| VA-COLOR-BRAND | 语义色可见性 | Token 名对照 | 同 L2 | — |
| VA-COLOR-GRADIENT | 有无渐变 | baseline.gradients | `background-image` | 稿无渐变 |
| VA-COLOR-OPACITY | — | baseline rgba alpha | `opacity` | — |
| VA-FONT-FAMILY | — | baseline typography | `fontFamily` | — |
| VA-FONT-SIZE | — | baseline size | `fontSize` | — |
| VA-FONT-WEIGHT | — | baseline weight | `fontWeight` | — |
| VA-FONT-LINEHEIGHT | — | baseline lineHeight | `lineHeight` | — |
| VA-FONT-LETTER-SPACING | — | 稿有指定则比 | `letterSpacing` | 稿未指定 |
| VA-FONT-DECORATION | — | 下划线/大小写 | `textDecoration` | 稿未指定 |
| VA-SPACING-BOX | — | baseline spacing | padding/margin/gap | — |
| VA-SPACING-GRID | 列数/栅格 | 帧宽与列定义 | — | — |
| VA-SPACING-ALIGN | 错位肉眼 | — | 同列 left 差 ≤1px | — |
| VA-LAYOUT-MISSING | 模块树对比 | components 列表 | — | — |
| VA-RADIUS | 圆角肉眼 | baseline radius | `borderRadius` | — |
| VA-SHADOW | 阴影肉眼 | baseline shadows | `boxShadow` | 稿无阴影 |
| VA-SHADOW-MULTI | — | 多层 shadow | 逐层解析 | 单层阴影 |
| VA-ICON-SIZE | 尺寸目测 | icons w/h | 元素 box | — |
| VA-ICON-RATIO | 拉伸目测 | 宽高比 | box 比 | — |
| VA-ICON-RESOLUTION | 边缘模糊 | — | 2x 截图 | 无位图 |
| VA-ICON-SVG | — | assetRef/path | — | 全 raster |
| VA-ICON-CROP | 裁剪对齐 | — | 截图 | — |
| VA-ICON-CLARITY | 轻微模糊 | — | 截图 | — |
| VA-ICON-FUNCTION | 语义对比 | 组件 name | — | — |

## checkpoint_ledger 填写规则

```yaml
# pass 示例
- checkpoint_code: VA-FONT-SIZE
  status: pass
  inspected: 4
  passed: 4
  failed: 0
  raw_deduction: 0
  final_deduction: 0
  note: "MasterGo Title/Body 4 锚点一致"

# na 示例
- checkpoint_code: VA-COLOR-GRADIENT
  status: na
  note: "验收帧无渐变样式"

# untested — 仅当缺 MasterGo 且无 URL，且用户接受
- checkpoint_code: VA-SHADOW
  status: untested
  note: "缺 URL，阴影五参数未 CDP 抽测"
```

**禁止**：未执行 L1/L2 抽样就直接 `untested`。

## verified_by 取值

| 值 | 含义 |
|----|------|
| `mastergo_dsl` | 设计值来自 MasterGo baseline |
| `screenshot` | 开发截图肉眼/布局对比 |
| `devtools` | CDP computedStyle |
| `untested` | 未验证，不计分 |

## 输出文件

```
reports/visual-acceptance-<page>-<date>/
├── design-baseline-raw.json    # MCP 原始 DSL
├── design-baseline.json        # 归纳后的期望值
├── styles-audit.json           # L2/L3 抽测记录（含 pass）
├── findings.json               # 仅 fail
├── annotated-dev.png
└── visual-acceptance-*.html
```
