# visual-acceptance-check
设计稿视觉还原度检查
> **中文** ｜ 一个面向前端/设计走查的 Skill：以 **MasterGo 设计稿 DSL** 为基准，对比 **开发页面截图**，按《视觉验收》PDF 的 **24 项 `VA-*` 检查点** 逐点 `pass / fail / na` 计分，并自动生成带 **bbox 标注** 的 HTML 验收报告。
> 

> 
> 

> **EN** ｜ A skill for front-end / design visual QA: it uses the **MasterGo design DSL** as the baseline, compares it against **development screenshots**, scores every one of the **24 `VA-*` checkpoints** (`pass / fail / na`) defined in the *Visual Acceptance* PDF, and auto-generates an HTML report with **bbox annotations**.
> 

---

## ✨ 这是什么 / What It Is

**中文**

`visual-acceptance-check` 解决“开发页面和设计稿到底差在哪、差多少”的问题。它不靠肉眼估算，而是：

- 从 **Figma/MasterGo 链接** 拉取 DSL，提取设计基准（尺寸 / Token / 组件 / 图标）；
- 用 **CDP（Chrome DevTools Protocol）** 精确抽测开发页面的间距、圆角、阴影、字体；
- 按 24 项视觉检查点逐条判定，输出可追溯的扣分明细与 **像素级 bbox 标注**；
- 一键生成 HTML 验收报告（设计侧链接 + 开发侧标注图并排展示）。

> 触发场景：视觉验收、MasterGo、设计稿链接、上传截图、页面截图、视觉差异、全量检查点、验收报告。
> 

**EN**

`visual-acceptance-check` answers the question: *“where and how much does the implementation deviate from the design?”* — without eyeballing. It:

- Pulls the DSL from a **MasterGo link** to extract the design baseline (dimensions / tokens / components / icons);
- Uses **CDP (Chrome DevTools Protocol)** to precisely sample spacing, border-radius, shadows, and fonts on the dev page;
- Judges each of the 24 visual checkpoints and outputs traceable deductions with **pixel-level bbox annotations**;
- Generates an HTML report in one step (design-side link + dev-side annotated image, side by side).

> Trigger when the user mentions: visual acceptance, MasterGo, design link, uploaded screenshot, page screenshot, visual diff, full checkpoint list, acceptance report.
> 

---

## 🚀 核心特性 / Features

**中文**

- **设计基准来自 DSL，而非猜测** — 文案 / Token 仅引用 MasterGo DSL，每条 `fail` 可回溯到 `styleId`。
- **三层走查（L1 / L2 / L3）**
    - **L1 宏观**：模块是否缺失、布局是否正确。
    - **L2 Token**：颜色 / 字号 / 间距等 Token 比对（文案差异仅记为观察项，不扣分）。
    - **L3 精测**：CDP 抽测字体、阴影、渐变，取最内层文字节点，避免取错父级。
- **24 项全量计分** — `checkpoint_ledger` 固定 24 行，禁止无理由 `untested`。
- **防误判护栏** — 路由 / 端型 / 采图 / DSL / CDP 取样均有规范。
- **可读的 HTML 报告** — H5 长页 375px 居中限高滚动，设计侧链接可点、无破图。

**EN**

- **Baseline from DSL, not guesswork** — copy & tokens are referenced only from the MasterGo DSL; every `fail` is traceable to a `styleId`.
- **Three-layer walkthrough (L1 / L2 / L3)**
    - **L1 Macro**: missing modules and layout correctness.
    - **L2 Tokens**: color / font-size / spacing token comparison (copy-only differences are recorded as observations, not deducted).
    - **L3 Precision**: CDP samples fonts, shadows, gradients — taking the innermost text node to avoid hitting the wrong parent.
- **Full 24-checkpoint scoring** — the `checkpoint_ledger` has a fixed 24 rows; no `untested` without justification.
- **Anti-misjudgment guardrails** — rules for routing, device type, capture, DSL, and CDP sampling.
- **Readable HTML report** — long H5 pages are centered at 375px with capped scrollable height; design-side links are clickable with no broken images.

---

## 📦 依赖与前置条件 / Requirements

| 依赖 / Dependency | 说明 / Description |
| --- | --- |
| `user-mastergo-magic-mcp` | 通过 `mcp__getDsl` 解析 MasterGo 链接，获取设计 DSL / Resolves the MasterGo link via `mcp__getDsl` to fetch the design DSL |
| Chrome + CDP | 视口模拟与 L3 精确抽测 / Viewport emulation and L3 precise sampling |
| Python 3 | 运行报告与标注脚本 / Runs the report & annotation scripts |

---

## 🔧 安装 / Installation

```bash
# 放置到 Cursor skills 目录 / Place under your Cursor skills directory
git clone <repo-url> ~/.cursor/skills/visual-acceptance-check
```

中文：脚本位于 `scripts/`，参考文档位于仓库根目录的各 `*.md`。

EN: Scripts live in `scripts/`; reference docs are the `*.md` files at the repo root.

---

## 📥 输入 / Inputs

| 必填 / Required | 说明 / Description |
| --- | --- |
| **MasterGo 链接 / MasterGo link** | 指向整页验收 Frame（含 `layer_id` 或短链）/ Points to the full-page acceptance frame (with `layer_id` or short link) |
| **开发截图 / Dev screenshot** | 已登录、与设计帧同宽高的 PNG（推荐本机截取）/ Logged-in PNG with the same width & height as the design frame (local capture recommended) |

| 可选 / Optional | 说明 / Description |
| --- | --- |
| 开发 URL / Dev URL | 供 CDP 精确抽测；登录态需人工 / For precise CDP sampling; login handled manually |
| MasterGo 导出 PNG / Exported PNG | DSL 无数图时用于报告并排展示 / Used for side-by-side display when the DSL lacks imagery |

> ⚠️ **不推荐 / Not recommended**：仅肉眼扫截图、不拉 MasterGo DSL，会导致 20+ 项 `untested`。 / Eyeballing screenshots without pulling the MasterGo DSL will leave 20+ items `untested`.
> 

---

## 🧭 工作流 / Workflow

```
0. 读开验前清单 / Read the pre-check list in acceptance-guardrails.md
1. MasterGo 拉 DSL → design-baseline.json（文案/Token 仅引 DSL）
   Pull DSL → design-baseline.json (copy/tokens referenced from DSL only)
2. 确认路由与端型 / Confirm routing & device (H5: /app/ + iPhone UA; bodyW ≈ innerWidth)
3. 采图 / Capture: CDP clip = frame.width; PNG width ≈ width × DPR
4. L1 宏观 + L2 Token（24 项 pass/fail/na；文案差异先记观察项）
   L1 macro + L2 tokens (24 items; copy diffs go to observations first)
5. L3 CDP：字体/阴影/渐变取最内层文字或卡片本体
   L3 CDP: sample font/shadow/gradient on the innermost text or card body
6. 计分 + checkpoint_ledger（禁止无理由 untested）
   Score + ledger (no unjustified untested)
7. 输出 / Output: HTML report + annotated-dev.png + report-meta.json
```

**关键约束 / Key constraints**

- **视口对齐 / Viewport alignment**：`dev` 与 `frame` 宽高误差 ≤2% 才做 px 级验收，否则 L2 标 `untested`。 / Only do px-level acceptance when `dev` vs `frame` differs by ≤2%; otherwise mark L2 as `untested`.
- **H5 采图 / H5 capture**：打开生产链接（如 `/app/`），勿用 `/fips/` 桌面路由；用 `Emulation.setUserAgentOverride`（iPhone）+ `setDeviceMetricsOverride`，再用 `Page.captureScreenshot` + `clip.width = frame.width`。 / Open the production link (e.g. `/app/`), not the `/fips/` desktop route; emulate iPhone UA + device metrics, then capture with `clip.width = frame.width`.
- **登录态 / Login**：SSO / 验证码须人工，`resolved_url` 写入 `report-meta.json`。 / SSO / captcha require manual steps; write `resolved_url` into `report-meta.json`.

---

## 📊 计分与 finding 格式 / Scoring & Finding Format

中文：`ledger` 固定 24 行；`untested` 仅在 L3 且缺 URL 时允许，且必须写 `note`。

EN: The `ledger` is fixed at 24 rows; `untested` is allowed only at L3 when the URL is missing, and must include a `note`.

```yaml
id: F-003
checkpoint_code: VA-COLOR-BRAND
severity: general
deduction: 1
region: "待办表-审批中状态点"     # region: "todo table - 'in approval' status dot"
bbox_px: [545, 162, 78, 16]
design: "MasterGo semantic/warning → #F5A623"
actual: "截图取样 → 蓝色 #1890FF"   # actual: sampled from screenshot → blue #1890FF
fix: "使用 Token semantic/warning"  # fix: use token semantic/warning
verified_by: mastergo_dsl
```

---

## 🖼️ 生成报告 / Generating the Report

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

中文：`REPORT_DATA` 必填字段：`designLink`、`designFrame`、`viewportMode`（H5 填 `"mobile"`）、`image_size`（与截图像素一致）。优先用脚本生成，**勿手改** `REPORT_DATA`；仅有 MasterGo 链接时写 `designLink` + `designFrame`，禁止空 `designImageBase64` 触发破图。

EN: Required `REPORT_DATA` fields: `designLink`, `designFrame`, `viewportMode` (`"mobile"` for H5), and `image_size` (matching the screenshot pixels). Prefer the scripts and **do not hand-edit** `REPORT_DATA`; when only a MasterGo link is available, set `designLink` + `designFrame` and never leave an empty `designImageBase64` (it causes broken images).

---

## 📁 仓库结构 / Repository Structure

```
visual-acceptance-check/
├─ SKILL.md                      # Skill 主定义 / Skill definition
├─ rules-reference.md            # 检查点与扣分 / Checkpoints & deductions
├─ scoring-algorithm.md          # 计分与 ledger / Scoring & ledger
├─ mastergo-baseline.md          # MasterGo 链接 → 设计基准 / Link → baseline
├─ full-checkpoint-checklist.md  # 24 项全量走查 / Full 24-item walkthrough
├─ annotation-guide.md           # bbox 标注 / bbox annotation
├─ acceptance-guardrails.md      # 防误判护栏 / Anti-misjudgment guardrails
├─ report-generation.md          # HTML 报告 / HTML report
├─ examples.md                   # 示例 / Examples
└─ scripts/
   ├─ generate-report.py
   └─ bake-annotations.py
```

---

## 🔀 与 design-fidelity-audit 的区别 / vs. design-fidelity-audit

| 项目 / Item | 本 skill / This skill | design-fidelity-audit |
| --- | --- | --- |
| 设计源 / Design source | **MasterGo 链接 DSL** 为主 / Mainly **MasterGo DSL** | PNG / Figma |
| 编码 / Coding | `VA-*`（24 项视觉 / 24 visual items） | `V/I/A-*`（三维度 / 3 dimensions） |
| 计分 / Scoring | 单维度 100 / Single dimension, 100 | 加权 40/35/25 / Weighted 40/35/25 |

---

## ✅ 输出检查清单 / Output Checklist

- [ ]  已读并执行开验前清单 / Pre-check list in `acceptance-guardrails.md` done
- [ ]  产出 `design-baseline.json` + `report-meta.json`（含 `resolved_url`、`capture_method`）/ Produced with `resolved_url` & `capture_method`
- [ ]  24/24 checkpoint 均有 `pass/fail/na`（`untested` 有 `note`）/ All 24 scored (`untested` carries a `note`)
- [ ]  所有 `fail` 项均含 `bbox_px`；`design` 引 MasterGo DSL / Every `fail` has `bbox_px`; `design` cites the DSL
- [ ]  HTML 报告：H5 截图限高可滚动；设计侧链接可点、无破图 / Report: scrollable capped H5 shot; clickable design link, no broken image
- [ ]  CDP 字体/阴影/渐变取样符合 guardrails §C / CDP sampling complies with guardrails §C
- [ ]  文案变更已区分：观察项 / 已确认正式需求 / fail / Copy changes classified: observation / confirmed requirement / fail

---

## 🤝 贡献 / Contributing

中文：欢迎提交 Issue 与 PR。修改检查点或计分逻辑时，请同步更新 `full-checkpoint-checklist.md` 与 `scoring-algorithm.md`，并在 `examples.md` 补充示例。

EN: Issues and PRs welcome. When changing checkpoints or scoring logic, update `full-checkpoint-checklist.md` and `scoring-algorithm.md`, and add an example to `examples.md`.

## 📄 License

MIT
