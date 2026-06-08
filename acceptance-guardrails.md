# 验收防误判指南

本文档来自首页 H5 生产验收复盘。**后续任意页面**执行本 skill 前必读，与 [full-checkpoint-checklist.md](full-checkpoint-checklist.md) 并列执行。

## 原则

1. **设计值只来自 MasterGo DSL** — 禁止凭印象写 `design` 字段；每个文案/Token 须能指向 DSL 节点或 styleId。
2. **先确认「验的是哪一页、哪条路由、哪种端」** — 再比 Token；路由/端型错误会导致整页误判。
3. **CDP 抽测取「可见文字/卡片本体」** — 不取布局父级容器的继承样式。
4. **文案差异 ≠ 模块缺失** — 模块在、仅改名 → 观察项，不自动扣分；产品确认正式需求后关闭。
5. **fail 必须可复现** — 记录 DOM 选择器、`getComputedStyle` 快照、DSL 引用；复核时能一键重跑。

---

## A. 路由与端型（开验前必做）

| 检查项 | 通过标准 | 常见误判 |
|--------|----------|----------|
| 入口 URL | 与用户给的**生产/H5 链接一致**（如 `/app/`） | 落到 `/fips/` 桌面端仍当 H5 验 |
| 移动端 UA | H5 帧须设 **iPhone UA** + `width = frame.width` | 仅缩视口、未切 UA，仍渲染桌面布局 |
| 布局宽度 | `body.scrollWidth ≈ innerWidth`（误差 ≤2%） | `bodyW=1660` 而 `innerW=375` 仍做 px 级 pass/fail |
| 落地页 | 记录 `location.href` 写入报告 meta | 登录页、404、空白 `/app/` 未加载完 |

**H5 推荐采图**

```
Emulation.setUserAgentOverride(iPhone)
Emulation.setDeviceMetricsOverride(width=375, mobile=true, dpr=3)
打开 /app/… → 等待 innerText 含关键模块
Page.captureScreenshot clip: { x:0, y:0, width:375, height:scrollHeight, scale:1 }
```

**禁止**仅用 `browser_take_screenshot` 作为 H5 唯一依据 — 易按浏览器面板宽度出图（如 1532px 宽 + 右侧白边）。

**PNG 宽度自检**：`imageWidth ≈ frame.width × DPR`（375×3 → **1125px**）。

---

## B. MasterGo DSL 提取（禁止猜设计）

### 文案 / 模块名

- 从 DSL **TEXT 节点**或 `text: [{ font: 'font_x:y', text: '…' }]` 读取，不要扫父 Frame 名凑合。
- **底部 Tab**：必须打开 `底部TAB` 帧下 3 个 TEXT（示例：首页 / 工作台 / 我的）。
- **快捷入口 vs 顶栏 Tab**：设计稿里可能是不同区域（如「常用功能」宫格 vs 状态栏下 Tab），**不得混为一项**比较。

### Token / 样式

- 颜色/阴影/渐变：读 `styles` 里 `paint_*` / `effect_*`，并定位**绑在哪个节点**（如渐变在 `导航背景` 而非 `body`）。
- 字体：读 `font_*` 的 `value.size` / `weight` / `lineHeight`；TEXT 通过 `text` 字段关联 fontId。

### 产品需求已变更

- DSL 仍为旧文案、产品已确认新文案 → 写入 `observations.json`，`status: closed_confirmed`，**不扣分**。
- 在 `design-spec-extract.json` 保留 `labels_mastergo_legacy` 与 `labels_official`。

---

## C. CDP 抽测：选对 DOM 节点

### 字体（VA-FONT-*）

| 场景 | 错误取样 | 正确取样 |
|------|----------|----------|
| 区块标题 | `.card-head`、`.title` 外层 div | **`span.title-name`**（或最内层含标题文字的节点） |
| Tab 文案 | 整块 tab 容器 | 激活态 **文字节点** 或 `.tab-item.active` |
| 底部 Tab | `.van-tabbar` 容器 | **`.van-tabbar-item` 内文字** |

父级常为 `font-weight: 400`，内层标题为 `600` — 只测父级会**系统性低估字重**。

### 阴影（VA-SHADOW*）

- 对照 DSL 中带 `effect_6:568`（S3）等的**白卡片矩形**，抽 **`pro-title-card`**（或等价卡片根）的 `boxShadow`。
- Tab 激活态阴影可能在**子元素**（如 `effect_6:373`），与卡片阴影分开记录。

### 背景渐变（VA-COLOR-GRADIENT）

- 抽 **实际承载 `background-image` 的节点**（如 `.home-page`），不要只看 `document.body`。
- 色 stop 一致、仅 **角度** 不同 → 默认观察项，不自动扣分，除非设计明确要求角度零容差。

---

## D. 扣分 vs 观察项 vs na

| 情形 | 处理 | ledger |
|------|------|--------|
| 模块设计有、实现无 | fail（VA-LAYOUT-MISSING） | fail + 扣分 |
| 模块在、文案与 DSL 不同 | **观察项**，待产品/设计确认 | pass / note |
| 产品确认正式需求 | 关闭观察项，更新 spec | pass |
| Token 量值不符（hex/px/shadow 五参数） | fail，须 CDP 证据 | fail + 扣分 |
| DSL 未指定（字间距等） | na | final_deduction=0 |
| 仅 L3 可测且缺 URL | untested + note | 不扣分 |

**禁止**：未跑 DSL + 未跑 CDP 就批量 `untested`（L1/L2 能测的必须测）。

---

## E. 开验前清单（复制执行）

```
- [ ] mcp__getDsl 已拉取，design-baseline.json 已生成
- [ ] 生产 URL 已打开，meta 记录最终 href
- [ ] H5：iPhone UA + innerWidth = frame.width，body.scrollWidth 对齐
- [ ] 截图 PNG 宽度 ≈ frame.width × DPR
- [ ] innerText 含设计稿关键模块（底部 Tab、主区块标题等）
- [ ] 文案对照来自 DSL TEXT，非猜测
- [ ] CDP 字体/阴影/渐变已抽最内层/正确卡片节点
- [ ] 24 项 ledger 均有 pass/fail/na/untested（untested 有 note）
- [ ] 每条 fail 的 design 可指向 MasterGo styleId 或节点名
```

---

## F. 首页复盘：曾出现的误判（勿重复）

| 误判 | 根因 | 正确做法 |
|------|------|----------|
| 底部 Tab 写成「消息」 | 未读 DSL | 读 `底部TAB` 下 TEXT：首页/工作台/我的 |
| 整页缺模块、84 分 | 验了 `/fips/` 桌面端 | 验 `/app/` + iPhone UA |
| 截图不像 H5 宽 | 面板截图非 clip 375 | CDP `captureScreenshot` clip |
| 背景「无渐变」 | 只看了 body | 看 `.home-page` background-image |
| 标题字重 400 | 测了 `.card-head` | 测 `span.title-name` → 600 |
| 快捷入口 vs 顶栏 Tab 混比 | 区域混淆 | 常用功能宫格单独对照 DSL |
| 科创项目库/参股基金扣分 | 未等产品确认 | 观察项 → 确认后关闭 |

---

## G. 报告必写字段

`report-meta.json` 建议包含：

```json
{
  "production_url": "用户入口",
  "resolved_url": "最终 href",
  "capture_method": "CDP clip 375px + iPhone UA",
  "viewport": { "width": 375, "dpr": 3 },
  "image_size": [1125, 5298],
  "methodology": "DSL 逐项 + CDP 最内层文字节点",
  "requirements_confirmed": [],
  "corrections": []
}
```

每次撤销误判，写入 `corrections[]` 便于审计追溯。
