# MasterGo 设计基准提取

将 MasterGo 链接转为验收用的 **design-baseline**，供 24 个 VA-* 检查点对照。平台细节见 [ds-from-design-link](/Users/hz-mb-0020/.cursor/skills/ds-from-design-link/SKILL.md) 的 MasterGo 章节。

## 链接解析

| URL 形式 | 提取 |
|----------|------|
| `https://{domain}/file/{fileId}?layer_id={layerId}` | `fileId` + `layerId` |
| `https://{domain}/goto/xxx` | 作为 `shortLink` 传给 `mcp__getDsl` |
| 含 `source_layer_id` | 优先用 `sourceLayerId` |

**验收帧**：用户链接必须指向**整页 Frame**（与开发页面对应的状态），不是单个组件或 Page 根节点（除非整页即 Frame）。

## MCP 调用顺序

1. **`mcp__getDsl`**（必选）— `shortLink` 或 `fileId` + `layerId`  
   - 保存返回 JSON 到 `reports/<page>/design-baseline-raw.json`  
   - **严格遵守** 返回中的 `rules` 字段  
2. **`mcp__getMeta`**（可选）— 仅当 DSL 缺页面级规则或需站点 meta 时

MCP 未连接：阻塞并列出检查项（登录 MasterGo、插件、文件权限）；**禁止编造**设计值。

## 从 DSL 提取 baseline 字段

解析 DSL 组件树，对**验收帧**及其子节点归纳：

```yaml
frame:
  name: "首页-默认态"
  width: 1920
  height: 960
  source: "mastergo://file/xxx?layer_id=yyy"

tokens:                    # 去重后的设计值清单
  colors: []               # { name, hex, rgba, usage }
  gradients: []            # { stops, angle, type }
  typography: []           # { name, family, size, weight, lineHeight, letterSpacing }
  spacing: []              # { name, padding, margin, gap }
  radius: []               # { name, value }
  shadows: []              # { layers: [{ x, y, blur, spread, color, opacity }] }

components:                # 关键模块边界（用于 LAYOUT 与 bbox 对照）
  - id: "nav"
    name: "顶栏"
    bbox: [0, 0, 1920, 56]
  - id: "tabs"
    name: "页签栏"
    bbox: [0, 56, 1920, 40]
  # … 3–8 个区域

icons: []                  # { name, width, height, assetRef, svgPath? }
```

**映射到检查点**：

| DSL 字段 | VA-* 检查点 |
|----------|-------------|
| `tokens.colors` | VA-COLOR-HEX, VA-COLOR-BRAND, VA-COLOR-OPACITY |
| `tokens.gradients` | VA-COLOR-GRADIENT |
| `tokens.typography.*` | VA-FONT-* |
| `tokens.spacing.*` | VA-SPACING-BOX, VA-SPACING-ALIGN |
| 帧宽 + 栅格列 | VA-SPACING-GRID |
| `components` 列表 | VA-LAYOUT-MISSING |
| `tokens.radius` | VA-RADIUS |
| `tokens.shadows` | VA-SHADOW, VA-SHADOW-MULTI |
| `icons.*` | VA-ICON-* |

## 设计稿预览图（报告用）

优先级：

1. MasterGo 导出 PNG / DSL 内嵌预览 URL（若有）→ `designImageBase64`  
2. **仅 MasterGo 链接**：报告写入 `designLink`（`frame.source`）+ `designFrame`；模板显示**可点击链接卡片**，**隐藏空 `<img>`**  
3. 用户额外上传的设计 PNG  

**禁止**：`designImageBase64: ""` 且仍渲染 `<img src="">` — 会显示破图且链接不可见。

生成报告时使用 [scripts/generate-report.py](scripts/generate-report.py)，自动从 `design-baseline.json` 填充 `designLink` / `designFrame`。

## 与开发截图对齐

```
scale_x = dev_width / frame.width
scale_y = dev_height / frame.height
```

- `scale_x ≈ scale_y ≈ 1`（误差 ≤2%）→ 可直接比对 px  
- 否则：**禁止**对间距/字号做 px 级 fail 判定；仅做布局/模块级 L1；在报告 meta 标注「视口未对齐，Token 抽测待重采」

## design 字段写法（findings）

有 baseline 时，`design` 必须引用可追溯来源：

```yaml
design: "MasterGo token color/brand-primary → #F5A623"
design: "MasterGo 文本样式 Title/14/Medium → 14px / 500 / 22px"
design: "MasterGo 卡片 radius-md → 8px"
```

无 baseline 条目时不得伪造；该检查点保持 `untested` 并写入待补测。
