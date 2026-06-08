# 视觉验收计分算法

本 skill 为**单维度**计分（仅视觉要素），不采用三维度加权。

## 流程概览

```
收集差异 → 应用单条扣分 → 应用重复/系统性规则 → 汇总 checkpoint_ledger
→ 得视觉分 → 等级判定 → 一票否决修正 → 输出报告
```

## Step 1：结构化差异

每条差异至少包含：

```yaml
id: F-003
checkpoint_code: VA-COLOR-GRADIENT
checkpoint_name: 颜色-渐变
severity: general | major | fatal
deduction: number
root_cause: gradient-brand-title
region: "主标题 ChatBI"
bbox_px: [547, 198, 115, 36]
label: 1
image_size: { width: 1440, height: 900 }
design: "linear-gradient #fc6506 → #fc8506"
actual: "纯色 #ff7a00"
evidence: "标题缺少渐变"
fix: "使用 --gradient-brand-text"
verified_by: mastergo_dsl | screenshot | devtools | untested
```

**verified_by 含义**：

| 值 | 设计值来源 | 实际值来源 |
|----|-----------|-----------|
| `mastergo_dsl` | MasterGo baseline | 截图/CDP 抽样 |
| `screenshot` | 截图对比 | 开发截图 |
| `devtools` | MasterGo baseline | CDP computedStyle |
| `untested` | — | 未验证，**不计分** |

`untested` 仅允许：缺 URL 且该检查点必须 L3；须在 ledger.note 说明。有 MasterGo baseline 时，颜色/字体类不得整体 untested。

## Step 2：检查点扣分明细账（checkpoint_ledger）

报告**必须**输出 `checkpoint_ledger`：对编码表中**每一个** `VA-*` 检查点一行（含未检测项）。

```yaml
checkpoint_ledger:
  - checkpoint_code: VA-COLOR-GRADIENT
    checkpoint_name: 颜色-渐变
    status: pass | fail | partial | untested | na
    inspected: 3
    passed: 2
    failed: 1
    raw_deduction: 1
    adjustment: 0
    final_deduction: 1
    finding_ids: [F-001]
    note: ""
```

**status 判定**：
- `pass`：inspected ≥ 3（或该页该类元素不足 3 则 inspected = 实际数量）且 failed = 0；须有 `styles-audit.json` 或 ledger.note 证据
- `fail`：failed > 0 且 final_deduction > 0
- `partial`：部分样本通过
- `untested`：**仅** L3 缺 URL；final_deduction = 0，note 必填
- `na`：本页不适用（如稿无渐变），final_deduction = 0，note 说明原因

**禁止**：未执行 [full-checkpoint-checklist.md](full-checkpoint-checklist.md) 抽样就将检查点标为 untested。

## Step 3：单维度计分

```
total_deduction = sum(entry.final_deduction for entry in checkpoint_ledger)
score = max(0, 100 - total_deduction)
```

### 重复/系统性调整（写入 ledger.adjustment）

| 规则 | 触发条件 | 调整 |
|------|----------|------|
| 字体系统性 | 同参数 ≥5 处 | 该 root_cause 合计 −7 封顶 |
| 间距系统性 | 同 Token ≥5 处 | −7 封顶 |
| 间距页面级 | 不同 Token 合计 ≥5 处 | 额外 −2 |
| 组件 Token | 同组件 Token ≥5 处 | −7 封顶 |
| 资源文件 | 同资源同错误 ≥3 处 | min(单次最大×3, 9) |
| 文本块叠加 | 同文本块 ≥3 类偏差 | 额外 −1 |

## Step 4：等级判定

```python
def grade(score):
    if score >= 95:
        return "优秀"
    if score >= 90:
        return "达标"
    if score >= 80:
        return "有条件通过"
    return "不达标"
```

## Step 5：一票否决修正

按顺序应用，取**最严格**结果：

1. **致命问题**：任一 `severity: fatal` → 等级上限「有条件通过」。
2. **颜色重复**：同一颜色错误 ≥3 次 → 等级上限「有条件通过」。

等级顺序：`优秀 > 达标 > 有条件通过 > 不达标`

## Step 6：行动项分级

| 优先级 | 条件 |
|--------|------|
| 必改 | fatal / major / 导致「不达标」/ 颜色重复≥3 |
| 应改 | general 且影响主流程或品牌一致性 |
| 可延期 | 一般问题且等级已达「达标」及以上 |

## 计分示例

| ID | checkpoint_code | 严重度 | 扣分 |
|----|-----------------|--------|------|
| F-001 | VA-COLOR-GRADIENT | general | 1 |
| F-002 | VA-FONT-SIZE | general | 1 |
| F-003 | VA-SPACING-BOX | general | 1 |
| F-004 | VA-LAYOUT-MISSING | major | 2 |
| F-005 | VA-RADIUS | general | 1 |

**合计扣分**：−6 → **得分 94** → **达标**

若 F-001/F-006/F-007 均为颜色类错误（共 3 处）→ 触发颜色重复 ≥3 → 等级上限「有条件通过」。
