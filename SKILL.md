---
name: visual-acceptance-check
description: 通过 MasterGo 设计稿链接与开发页面截图（或登录后 URL 截图）按《视觉验收》PDF 全量 VA-* 检查点验收，从 DSL 提取设计基准、逐点 pass/fail/na 计分并 bbox 标注，输出 HTML 报告。Use when the user mentions 视觉验收、MasterGo、设计稿链接、上传截图、页面截图、视觉差异、全量检查点、验收报告。
disable-model-invocation: true
---

# 视觉验收

对比 **MasterGo 设计基准** 与 **开发页面截图**，按 [`视觉验收.pdf`](/Users/hz-mb-0020/Downloads/视觉验收.pdf) 视觉要素 **24 项 VA-* 检查点**验收，输出计分与标注报告。

## 必读参考

| 文件 | 用途 |
|------|------|
| [rules-reference.md](rules-reference.md) | 检查点与扣分 |
| [scoring-algorithm.md](scoring-algorithm.md) | 计分与 ledger |
| [mastergo-baseline.md](mastergo-baseline.md) | **MasterGo 链接 → 设计基准** |
| [full-checkpoint-checklist.md](full-checkpoint-checklist.md) | **24 项全量走查** |
| [annotation-guide.md](annotation-guide.md) | bbox 标注 |
| [acceptance-guardrails.md](acceptance-guardrails.md) | **防误判：路由/采图/DSL/CDP 取样** |
| [report-generation.md](report-generation.md) | **HTML 报告：H5 长页布局 + 设计链接展示** |
| [examples.md](examples.md) | 示例 |

## 推荐输入（MasterGo + 开发截图）

| 必填 | 说明 |
|------|------|
| **MasterGo 链接** | 指向整页验收 Frame（含 `layer_id` 或短链） |
| **开发截图** | 已登录、与设计帧 **同宽高** 的 PNG（推荐用户本机截取） |

| 可选 | 说明 |
|------|------|
| 开发 URL | CDP 精确抽测间距/圆角/阴影；需登录见下文 |
| MasterGo 导出 PNG | 报告并排展示设计稿（DSL 无数图时） |

**不推荐**：仅用肉眼扫截图且不拉 MasterGo DSL — 会导致 20+ 项 `untested`。

## 工作流

```
Task Progress:
- [ ] 0. 读 acceptance-guardrails.md 开验前清单
- [ ] 1. MasterGo 拉 DSL → design-baseline.json（文案/Token 仅引 DSL）
- [ ] 2. 确认路由与端型（H5：/app/ + iPhone UA；bodyW ≈ innerWidth）
- [ ] 3. 采图：CDP clip frame.width；PNG 宽 ≈ width×DPR
- [ ] 4. L1 宏观 + L2 Token（24 项 pass/fail/na；文案差异先观察项）
- [ ] 5. L3 CDP：字体/阴影/渐变取最内层文字或卡片本体（见 guardrails §C）
- [ ] 6. 计分 + checkpoint_ledger（禁止无理由 untested）
- [ ] 7. HTML 报告 + annotated-dev.png + report-meta.json
```

### Step 0：MasterGo 设计基准（必做）

1. 解析链接 → 调用 **`user-mastergo-magic-mcp`** 的 `mcp__getDsl`（见 [mastergo-baseline.md](mastergo-baseline.md)）
2. 归纳 `design-baseline.json`：`frame.width/height`、`tokens`、`components`、`icons`
3. 记录帧尺寸，作为开发截图/URL 视口的**目标宽高**

### Step 1：视口对齐

- `dev 宽/高` 与 `frame 宽/高` 误差 ≤2% → 可做 px 级 Token 验收  
- 否则：仅 L1 布局验收；L2 px 级标 `untested` 并注明「需重采同尺寸截图」

### Step 2：路由、端型与采图

详见 [acceptance-guardrails.md](acceptance-guardrails.md) §A–§C。

**H5 页面（MasterGo 帧宽 ≤480）**

1. 打开用户给的 **H5 生产链接**（如 `/app/`），**勿**用 `/fips/` 桌面路由代替  
2. `Emulation.setUserAgentOverride`（iPhone）+ `setDeviceMetricsOverride(width=frame.width)`  
3. 确认 `body.scrollWidth ≈ innerWidth` 且关键模块出现在 `innerText`  
4. **采图**：`Page.captureScreenshot` + `clip.width = frame.width`（PNG 宽 ≈ `width × DPR`）  
5. **勿**仅依赖 `browser_take_screenshot`（易按面板宽度出图、带白边）

**用户本机上传截图（推荐内网）**

1. DevTools 设备模式 → 与 MasterGo 帧同宽 → 只截视口  
2. Agent 校验 PNG 宽度 ≈ `frame.width × DPR` 后再验收  

**登录** — SSO/验证码须人工；记录 `resolved_url` 写入 `report-meta.json`

### Step 3：全量检查点走查

严格按 [full-checkpoint-checklist.md](full-checkpoint-checklist.md) 与 [acceptance-guardrails.md](acceptance-guardrails.md) §D：

- **L1**：DSL `components` + TEXT 文案 vs 截图/innerText → 模块**缺失**才 fail  
- **L2**：DSL Token vs 截图/CDP；**文案仅差异** → `observations.json`，不扣分，待设计/产品确认  
- **L3**：CDP 抽测间距/圆角/阴影；**字体取最内层文字节点**（如 `span.title-name`），不取 `.card-head` 父级  

每条 **fail** 须：`design` 可追溯 DSL styleId、`actual` 有 CDP 选择器、含 `bbox_px`。  
**pass** 写入 `styles-audit.json`。误判撤销写入 `report-meta.json` → `corrections[]`。

```yaml
id: F-003
checkpoint_code: VA-COLOR-BRAND
severity: general
deduction: 1
region: "待办表-审批中状态点"
bbox_px: [545, 162, 78, 16]
design: "MasterGo semantic/warning → #F5A623"
actual: "截图取样 → 蓝色 #1890FF"
fix: "使用 Token semantic/warning"
verified_by: mastergo_dsl
```

### Step 4：计分

见 [scoring-algorithm.md](scoring-algorithm.md)。ledger **24 行**；`untested` 仅 L3 且缺 URL 时允许，须写 `note`。

### Step 5：HTML 报告

见 [report-generation.md](report-generation.md)。

1. 产物目录 `reports/visual-acceptance-<page>-<timestamp>/`  
2. **设计侧**：有 PNG 则嵌入；**仅 MasterGo 链接时**写入 `designLink` + `designFrame`，**禁止**空 `designImageBase64` 触发破图  
3. **开发侧**：全页 PNG + SVG bbox；H5 长页在模板内 **375px 居中 + 限高滚动**（非整页拉满宽度）  
4. 优先用脚本生成，勿手改 `REPORT_DATA`：

```bash
SKILL=~/.cursor/skills/visual-acceptance-check
OUT=reports/visual-acceptance-<page>-<timestamp>

python3 "$SKILL/scripts/generate-report.py" \
  --dir "$OUT" \
  --title "<页面>视觉验收" \
  --meta "375×812 · H5 · $(date +%F)" \
  --dev dev.png \
  --baseline design-baseline.json \
  --findings findings.json \
  --ledger checkpoint-ledger.json

python3 "$SKILL/scripts/bake-annotations.py" \
  "$OUT/dev.png" "$OUT/findings.json" -o "$OUT/annotated-dev.png"
```

`REPORT_DATA` 必填字段：`designLink`、`designFrame`、`viewportMode`（H5 填 `"mobile"`）、`image_size` 与截图像素一致。

## 与 design-fidelity-audit 区分

| 项目 | 本 skill | design-fidelity-audit |
|------|----------|----------------------|
| 设计源 | **MasterGo 链接 DSL** 为主 | PNG / Figma |
| 编码 | `VA-*`（24 项视觉） | `V/I/A-*`（三维度） |
| 计分 | 单维度 100 | 加权 40/35/25 |

## 输出检查

- [ ] 已读并执行 [acceptance-guardrails.md](acceptance-guardrails.md) 开验前清单  
- [ ] `design-baseline.json` + `report-meta.json`（含 resolved_url、capture_method）  
- [ ] 24/24 checkpoint 有 pass/fail/na（untested 有 note）  
- [ ] fail 项均有 `bbox_px`；`design` 引 MasterGo DSL，非猜测  
- [ ] HTML 报告：H5 截图限高可滚动；设计侧链接可点、无破图（见 report-generation.md）  
- [ ] CDP 字体/阴影/渐变取样符合 guardrails §C  
- [ ] 文案变更已区分：观察项 / 已确认正式需求 / fail  
