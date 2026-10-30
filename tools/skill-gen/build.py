# -*- coding: utf-8 -*-
"""渲染 11 位新名人 skill（14 文件/人），并同步 registry 与 roundtable-matrix。"""
import os, json
from people import PEOPLE

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = os.path.join(ROOT, "skills")
REG = os.path.join(ROOT, "registry", "index.json")
MAT = os.path.join(ROOT, "registry", "roundtable-matrix.json")

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def fmt_list(items, numbered=False, lead="- "):
    out = []
    for i, it in enumerate(items, 1):
        if numbered:
            out.append(f"{i}. {it}")
        else:
            out.append(f"{lead}{it}")
    return "\n".join(out)

# ---------- 各文件渲染 ----------

def render_skill_md(p):
    cm = fmt_list([f"**{n}**——{d}" for n, d in p["core_models"]])
    comp = "、".join(p["complements"])
    desc = (f"以{p['person']}的{('、'.join(p['frameworks'][:3]))}与文风，对{p['domain_cn']}相关问题做深度分析。"
            f"触发：要求\"用{p['person']}的框架分析\"\"像{p['person']}那样想想\"\"{'、'.join(p['roundtable_tags'][:3])}\"；"
            f"或用户希望得到带有{p['style_keywords'][0]}特征的分析。本技能提供思维框架与文风，"
            f"不声称代表{p['person']}本人或其未公开观点。与聚焦{p['domain_cn']}互补领域的 {comp} 互补。")
    of = fmt_list(p["output_format"], numbered=True)
    return f"""---
name: {p['name']}
description: "{desc}"
agent_created: true
---

# {p['person']}思维框架与分析风格

## 目的

将 {p['person']} 的思维方法论与表述风格固化为可复用的分析流程，使本助手在回答{p['domain_cn']}问题时，能够：

1. 用 {p['person']} 的核心框架拆解问题
2. 以 {p['style_keywords'][0]} 的视角识别关键变量与陷阱
3. 输出带有 {p['person']} 文风特征的结构化研判

> 说明：本技能是**思维框架与文风的工具**，用于辅助用户自行研判。它不声称代表 {p['person']} 本人，也不引用或复制任何未公开的专有研究。所有数据判断应以实时信息为准。

{status_block(p)}
## 何时使用

- 用户明确要求"{p['person']}的框架""像{p['person']}那样""{'、'.join(p['roundtable_tags'][:3])}"等表述；
- 用户提出 {p['domain_cn']} 问题，且希望得到结构化、{p['style_keywords'][0]} 的分析；
- 需要识别 {p['roundtable_tags'][0]} 等维度的风险或机会。

**何时不使用**：
- 纯 {p['complements'][0]} 领域问题 → 优先用对应 skill；
- 只需一句话判断或纯数据查询 → 直接给数据；
- 需要多视角会诊 → 参见 `combos/` 下的圆桌会议方案。

## 核心思维模型（必须掌握）

分析任何问题前，先按问题性质选择最贴切的模型组合作为论述骨架。核心模型优先级：

{cm}

> 详细展开见 `references/01-core-theories.md`。

## 工作流

1. **前置判断**：明确问题类型、可调用数据与是否在本技能能力圈内。
2. **逆向检查（默认前置，不可跳过）**：先想"什么会让这个结论出错 / 导致失败"，再正向论证。
3. **取数（可选但建议）**：若环境内有金融数据工具，先拉取关键数据；取不到则声明"以下为框架性推演，缺乏实时数据校验"。
4. **多模型扫描**：套用核心思维模型逐层展开。
5. **偏误 / 风险扫描**：识别最可能的认知偏误或结构性风险。
6. **二阶追问**：对初步结论追问至少两轮"然后呢？"
7. **机会成本比较**：明确次优选择是什么。
8. **搭骨架 + 套文风**：用选定模型先给一句"核心判断"，再按文风规范分层展开。

## 文风规范

### 语气特征
{fmt_list(p['style_tone'])}

### 句式偏好
{fmt_list(p['style_sentence'])}

### 禁忌
{fmt_list(p['style_taboo'])}

### 文风示例

**正面**：{p['style_pos']}

**反面**：{p['style_neg']}

## 输出格式

{of}

## 协作声明

- 纯 {p['domain_cn']} → 用本技能
- 涉及互补领域 → 优先用 `{p['complements'][0]}` 等
- 需要多视角会诊 → 参见 `combos/` 下的圆桌会议方案
{ethics_block(p)}"""

def render_condensed(p):
    cm = fmt_list([f"**{n}**——{d}" for n, d in p["core_models"]])
    of = fmt_list(p["output_format"], numbered=True)
    return f"""---
name: {p['name']}-condensed
description: "[精简版] {p['person']} 框架快速调用。触发词与完整版一致。"
agent_created: true
---

# {p['person']}分析框架（精简版）

> 本文件是完整版 SKILL.md 的精简变体，约 5KB。需要深度分析时请切换至完整版。

## 定位声明

本技能是思维框架与文风的工具，不声称代表 {p['person']} 本人。

## 何时使用

- 用户要求"用{p['person']}的框架分析""像{p['person']}那样想想"
- 用户提出 {p['domain_cn']} 问题并希望以 {p['person']} 视角研判

## 核心框架（速览）

{cm}

> 详细展开见 `references/01-core-theories.md`

## 文风要点

- {p['style_tone'][0]}
- 招牌隐喻：{p['metaphor']}
- 招牌收尾：{p['ending']}

## 输出格式

{of}

## 合规

- 输出标注"按{p['person']}框架分析"，非"{p['person']}认为"
- 不构成投资建议

## 变体说明

| 变体 | 适用场景 |
|------|---------|
| SKILL.md（完整版） | 深度分析，全量框架 |
| **SKILL-condensed.md（本文件）** | 快速调用，省 token |

安装时将所需变体重命名为 SKILL.md 即可。
"""

def lifespan(p):
    """生卒行。living: True=在世 / False=已故 / None=待考或非人物（机构方法论）。"""
    if p.get("kind") == "methodology":
        return f"{p['born']} 年提出／持续更新"
    born = p.get("born") or ""
    living, died = p.get("living"), p.get("died")
    if living is True:
        return f"{born} / 在世（截至 {REPO_UPDATED}）"
    if living is False:
        return f"{born}–{died}"
    return "生年与卒年待考"


def status_block(p):
    """人物状态声明：已故者给纪念与伦理说明，在世者声明不代表当前观点。"""
    person = p["person"]
    if p.get("kind") == "methodology":
        by = p.get("by", "相关机构")
        return (f"> **条目性质**：本条目整理的是 {by}的方法论，"
                f"不是一位具体人物的思想档案，故不标注生卒。\n")
    living, died = p.get("living"), p.get("died")
    if living is False:
        return (f"> **人物状态**：{person} 已于 {died} 逝世（{p.get('born')}–{died}）。"
                f"本档案整理其生前公开发表的方法论与表述风格，其观点止于最后公开表达之时；"
                f"本档案为其方法的记录与致意，不声称代表其本人或其家属立场。\n")
    if living is None:
        return f"> **人物状态**：生年与卒年待考，本档案不对其做任何推断。\n"
    return (f"> **人物状态**：截至 {REPO_UPDATED}，{person} 在世。其观点会随时间变化，"
            f"本档案不代表其当前观点。\n")


def ethics_block(p):
    note = p.get("ethics_note")
    return f"\n> **使用限定**：{note}\n" if note else ""


def sources_line(p):
    """生卒与现任职务的依据。只在 people.py 填了 sources 时渲染——
    宁可留空，也不给没查证过的条目编一个出处。"""
    src = p.get("sources") or []
    if not src:
        return ""
    if len(src) == 1:
        return f"- **事实依据**：{src[0]}\n"
    return "- **事实依据**：\n" + "".join(f"  - {s}\n" for s in src)


def render_profile(p):
    src = fmt_list([f"- 《{t}》——框架提炼来源：{s}" for t, s in p["bio_sources"]])
    comp = fmt_list([f"- 与 `{c}` 互补：覆盖 {p['domain_cn']} 视角的不同侧面" for c in p["complements"]])
    return f"""# 人物档案卡：{p['person']}

## 基本信息

- **姓名**：{p['person']} / {p['person_en']}
- **生卒**：{lifespan(p)}
{sources_line(p)}- **国籍**：{p['nationality']}
- **领域**：{p['domain_cn']}
- **身份**：{p['identity']}

## 代表作与思想来源

{src}

## 框架来源声明

本 skill 的思维框架提炼自上述公开材料中的方法论与表述风格。不引用任何未公开的专有研究，不声称代表人物本人或其当前观点。所有数据判断应以实时信息为准。

{status_block(p)}{ethics_block(p)}
## 互补关系

{comp}

> 完整的互补关系映射见 `registry/index.json` 的 `complements` 字段。

## 免责声明

本技能是思维框架与文风的工具，用于辅助用户自行研判。它不声称代表 {p['person']} 本人，也不引用或复制任何未公开的专有研究。skill 中所有分析均为基于公开方法论的框架性推演，不构成投资建议。
"""

def render_citation(p):
    return f"""cff-version: 1.2.0
message: "如果您在研究中使用了本 SKILL，请按以下格式引用。"
title: "{p['person']} 思维框架 SKILL"
authors:
  - given-names: "SKILL Palace"
date-released: "2026-08-05"
version: "1.0.0"
keywords:
  - "AI Agent Skill"
  - "{p['domain_cn']}"
  - "{p['person']}"
license: MIT
repository-code: "https://github.com/kevin12369/skill-palace/tree/main/skills/{p['name']}"
abstract: >-
  将 {p['person']} 的思维方法论与表述风格固化为可复用的 AI Agent 技能。
  本技能是思维框架与文风的工具，不声称代表 {p['person']} 本人。
"""

def render_changelog(p):
    return f"""# Changelog

本文件记录 {p['person']} SKILL 的版本历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 扩充 examples/ 示例集

## [1.0.0] - 2026-08-05

### 新增
- 初始版本发布
- SKILL.md 完整版（核心框架 + 工作流 + 文风规范 + 输出模板）
- SKILL-condensed.md 精简版变体
- references/ 编号文件体系（01-08，含正反双校验）
- PROFILE.md 人物档案卡
- examples/ 示例索引
- CITATION.cff 学术引用格式

### 变更
- 无（首版）

### 已知问题
- 数据判断须以实时信息为准
"""

def render_examples_index(p):
    """索引以「目录里真实存在的文件」为准，不再把计划中的选题渲染成看起来可点的表格。

    历史问题：旧版把 people.py 里的选题直接渲染成 `example-01-xxx.md` 表格，但仓库里
    从来没有对应的示例正文，51 份 INDEX 共出现 102 条幻影引用。现在改为：状态由扫描
    目录得出，选题单列且与状态分离，二者不混淆。
    """
    exdir = os.path.join(SKILLS, p["name"], "examples")
    real = sorted(f for f in os.listdir(exdir)
                  if f.startswith("example-") and f.endswith(".md")) if os.path.isdir(exdir) else []
    if real:
        lines = "\n".join(f"| [{f}]({f}) | {os.path.getsize(os.path.join(exdir, f))} B |" for f in real)
        status = (f"本目录当前有 **{len(real)} 个**示例正文（由构建脚本扫描目录得出）：\n\n"
                  "| 文件 | 大小 |\n|------|------|\n" + lines)
        plan_head = "选题参考（历史规划；某条是否已落地，以上表实际文件为准）"
    else:
        status = ("本目录当前**没有**任何示例正文（此结论由构建脚本扫描目录得出，非手写）。\n\n"
                  "> 下节「规划选题」只是选题清单，**没有对应的示例文件**，"
                  "请勿当作已落地内容引用或链接。")
        plan_head = "规划选题（未落地）"
    plans = "\n".join(f"- **{t}** —— {n}" for (_f, t, n) in p["examples_index"])
    return f"""# 示例索引

> 本目录用于存放 {p['person']} skill 的示例输出：给用户看预期效果，给 Agent 校准风格。

## 当前状态

{status}

## {plan_head}

{plans}

## 示例编写规范

每个示例文件应包含：

1. **输入**：用户的问题/请求（原文）
2. **框架选择**：本示例调用了哪些核心框架
3. **完整输出**：Agent 的完整分析输出（符合文风规范）
4. **校准说明**：本示例如何通过 `07-checklist.md` 的校验

## 使用方式

- **人类用户**：浏览本目录了解 skill 的输出效果
- **Agent**：运行时不加载本目录（仅供参考），按 SKILL.md 和 references/ 执行
- **贡献者**：新增示例文件（命名 `example-NN-<topic>.md`）后重跑 `build.py`，本索引会自动列出。
  示例正文结尾必须写一段 `> **AI 生成声明**：……`（AI 撰写、经人工校对、不代表本人观点、
  不构成投资建议），缺了 `scripts/audit_skills.py` 的 EX-05 会报错，见 `SKILL_SPEC.md` §7。
"""

def render_ref01(p):
    parts = []
    for i, t in enumerate(p["theories"], 1):
        steps = fmt_list(t["steps"])
        parts.append(f"""## 理论 {i}：{t['name']}

### 定义
{t['def']}

### 适用场景
{t['scenario']}

### 操作步骤
{steps}

### 示例
{t['example']}

### 注意事项
{t['notes']}

---
""")
    head = (f"# 01 - 核心理论详解\n\n> 本文件详解 {p['person']} 的核心思维模型。"
            f"SKILL.md 中的\"核心思维模型\"区块在此展开为完整定义。\n\n")
    return head + "\n".join(parts)

def render_ref02(p):
    wf = """## 工作流详解

1. **前置判断**：问题类型与能力圈自检
2. **逆向检查（默认前置）**：先找失败/错误路径
3. **取数（可选）**：拉取关键指标校验框架
4. **多模型扫描**：套用核心框架分层展开
5. **偏误/风险扫描**：识别主要偏差或结构风险
6. **二阶追问**：至少两轮"然后呢？"
7. **机会成本比较**：明确次优选择
8. **输出**：核心判断 + 框架拆解 + 建议

---

"""
    det = "\n".join(f"## {n}\n\n{c}\n\n---" for n, c in p["frameworks_detail"])
    return f"# 02 - 分析框架与工作流\n\n> {p['person']} 的工作流与框架化分析工具。\n\n{wf}\n{det}\n"

def render_ref03(p):
    return f"""# 03 - 文风与语气规范

> 本文件校准 Agent 输出是否"像 {p['person']}"。

## 语气特征
{fmt_list(p['style_tone'])}

## 句式偏好
{fmt_list(p['style_sentence'])}

## 禁忌
{fmt_list(p['style_taboo'])}

## 招牌隐喻
{p['metaphor']}

## 文风示例

**正面**（符合文风）：
> {p['style_pos']}

**反面**（不符合文风）：
> {p['style_neg']}

## 招牌收尾
{p['ending']}

## 使用方式
输出前对照 `07-checklist.md` 逐项自检；不确定时偏向"承认无知 + 给框架"而非编造确定结论。
"""

def render_ref04(p):
    rows = "\n".join(f"| {y} | {e} |" for y, e in p["timeline"])
    return f"""# 04 - 关键观点与年表

> {p['person']} 的生平与思想演进关键节点。

| 年份 | 事件 |
|------|------|
{rows}

## 框架演进要点

- 早期：奠定核心方法论基础
- 中期：体系化并著书立说
- 后期：被广泛引用，成为 {p['domain_cn']} 领域的参照坐标

> 如人物已故，观点止于最后公开表达之时；数据判断须以实时信息为准。
"""

def render_ref05(p):
    rows = "\n".join(f"| 《{t}》 | {y} | {n} |" for t, y, n in p["publications"])
    return f"""# 05 - 代表著作与文献

> {p['person']} 框架的主要公开来源。

| 著作 | 年份 | 说明 |
|------|------|------|
{rows}

## 提炼说明

本 skill 的框架提炼自上述公开著作与演讲中的方法论与表述风格。不引用任何未公开的专有研究，不声称代表人物本人或其当前观点。
"""

def render_ref06(p):
    rows = "\n".join(f"| {t} | {d} |" for t, d in p["glossary"])
    return f"""# 06 - 术语表

> {p['person']} 框架中的关键术语速查。

| 术语 | 定义 |
|------|------|
{rows}
"""

def render_ref07(p):
    return f"""# 07 - 风格校准 Checklist

> 输出前必须逐项检查的正向校验清单。与 `08-style-anti-patterns.md`（反向校验）配合使用。

## 校准清单

### 内容校准

- [ ] **框架到位**：使用了 {p['person']} 的核心思维模型（非泛泛而谈）
- [ ] **数据/逻辑翔实**：引用具体机制或案例，而非空话
- [ ] **逻辑严密**：立论 → 举证 → 边界条件 → 不确定性，链路完整
- [ ] **逆向检查已做**：先想"什么会出错"再正向论证
- [ ] **讨论边界条件**：明确结论成立的前提
- [ ] **承认不确定性**：不装全知，标注判断置信度

### 风格校准

- [ ] **语气符合**：{p['style_tone'][0]}
- [ ] **句式符合**：{p['style_sentence'][0]}
- [ ] **招牌收尾**：{p['ending']}

### 合规校准

- [ ] **AI 模拟声明**：输出中标注"按 {p['person']} 框架分析"，而非"{p['person']} 认为"
- [ ] **免责声明**：不构成投资建议 / 不预测具体点位 / 不推荐具体标的
- [ ] **不虚构**：不编造未公开讲话或观点
- [ ] **时间边界**：如人物已故，观点止于最后公开表达之时

## 使用方式

```
输出前自检流程：
1. 完成 content 校准（6 项）
2. 完成 style 校准（3 项）
3. 完成 compliance 校准（4 项）
4. 全部通过 → 输出
5. 任一未通过 → 修正后重新自检
```
"""

def render_ref08(p):
    blocks = []
    for i, a in enumerate(p["anti_patterns"], 1):
        blocks.append(f"""## 反例 {i}：{a['type']}

### 错误输出
> {a['wrong']}

### 为什么不像
{a['why']}

### 正确改写
> {a['right']}

---
""")
    table = "\n".join(f"| {a['type']} | {a['wrong'][:24]}… | {a['right'][:24]}… |" for a in p["anti_patterns"])
    head = (f"# 08 - 风格反例库\n\n> \"什么不像 {p['person']}\"——反向校验库。"
            f"与 `07-checklist.md`（正向校验）配合使用。\n\n")
    return head + "\n".join(blocks) + f"""## 常见偏差速查

| 偏差类型 | 表现 | 纠正方向 |
|---------|------|---------|
{table}
"""

# ---------- registry & matrix ----------

# 仓库版本口径（单一来源）。index.json 与 roundtable-matrix.json 统一使用三段式，
# 避免此前 index 写 "2.5.0"、matrix 写 "2.5" 的格式分裂。发版只改这两行。
REPO_VERSION = "2.7.0"
REPO_UPDATED = "2026-10-30"

# 单一来源的 slug → 短代码 映射。slug（如 gao-shanwen）才是唯一主键；
# 短代码（如 GS）仅为「展示别名」，集中在此处维护，避免跨 4 个文件手动同步。
# 新增人物时在此追加一行即可；build 会自动做冲突检测。
CODE_MAP = {
    "gao-shanwen":"GS","greenspan":"GP","warren-buffett":"WB","charlie-munger":"CM",
    "carlota-perez":"CP","kondratiev":"KN","george-soros":"SZ","irving-fisher":"IF",
    "philip-fisher":"PF","hyman-minsky":"HM","ray-dalio":"RD","joseph-schumpeter":"SP",
    "theodore-wright":"WR","gartner-hype-cycle":"GT","william-jevons":"JV",
    "howard-marks":"HOM","burton-malkiel":"BM","fred-schwed":"FS","daniel-kahneman":"DK",
    "qiu-guolu":"QG","liu-shunren":"LS","john-gordon":"JG","robert-shiller":"RS",
    "charles-ellis":"CE","nassim-taleb":"NT","ben-bernanke":"BB",
    "duan-yongping":"DY","li-daxiao":"LD","hong-hao":"HH","peter-lynch":"PL","fu-peng":"FP","xu-xiang":"XX","beijing-chaojia":"BC",
    "jesse-livermore":"JL","william-gann":"WG","michael-steinhardt":"SH",
    "martin-schwartz":"MZ","larry-williams":"LW","joseph-granville":"GR",
    "richard-wyckoff":"RW","george-douglas-taylor":"GD","jeff-cooper":"JC",
    "yeshan-zhangwenhua":"YS","junshan-jushi":"JS","xu-wenming":"XW",
    "qin-guoan":"QA","long-qitian":"LQ","yang-jiyuan":"YJ",
    "james-simons":"JM",
    "stanley-druckenmiller":"SD","william-oneil":"WO"
}
STAGE_MAP = {
    "gao-shanwen":"宏观定调","greenspan":"宏观定调","kondratiev":"宏观定调","irving-fisher":"宏观定调",
    "ray-dalio":"宏观定调","george-soros":"宏观定调",
    "carlota-perez":"中观筛选","hyman-minsky":"中观筛选","joseph-schumpeter":"中观筛选",
    "gartner-hype-cycle":"中观筛选","theodore-wright":"中观筛选","william-jevons":"中观筛选",
    "charlie-munger":"中观筛选",
    "warren-buffett":"微观决策","philip-fisher":"微观决策",
    "howard-marks":"中观筛选","burton-malkiel":"中观筛选","fred-schwed":"中观筛选",
    "daniel-kahneman":"中观筛选","charles-ellis":"中观筛选","nassim-taleb":"中观筛选",
    "qiu-guolu":"微观决策","liu-shunren":"微观决策",
    "john-gordon":"宏观定调","robert-shiller":"宏观定调","ben-bernanke":"宏观定调",
    "duan-yongping":"微观决策","li-daxiao":"宏观定调","hong-hao":"宏观定调",
    "peter-lynch":"微观决策","fu-peng":"宏观定调","xu-xiang":"中观筛选","beijing-chaojia":"中观筛选",
    "jesse-livermore":"中观筛选","william-gann":"中观筛选","michael-steinhardt":"宏观定调",
    "martin-schwartz":"中观筛选","larry-williams":"中观筛选","joseph-granville":"中观筛选",
    "richard-wyckoff":"中观筛选","george-douglas-taylor":"中观筛选","jeff-cooper":"中观筛选",
    "yeshan-zhangwenhua":"中观筛选","junshan-jushi":"中观筛选","xu-wenming":"中观筛选",
    "qin-guoan":"中观筛选","long-qitian":"中观筛选","yang-jiyuan":"中观筛选",
    "james-simons":"中观筛选",
    "william-oneil":"中观筛选",
    "stanley-druckenmiller":"宏观定调"
}

def validate_maps():
    """建图前的守卫：两位映射表必须覆盖全部人物，短代码必须非空且唯一。

    历史教训：CODE_MAP 曾漏登记 stanley-druckenmiller / william-oneil，两人的 code
    变成空字符串，而「重复检测」只比较值是否重复，空字符串互不重复因而静默通过，
    最终表现为 alias_map 少人、前端缺别名。此函数把空值/缺项/孤儿项一并拦下。
    """
    from collections import Counter
    slugs = [p["name"] for p in PEOPLE]

    missing_stage = [s for s in slugs if s not in STAGE_MAP]
    if missing_stage:
        raise SystemExit(f"[STAGE MISSING] STAGE_MAP 未登记：{missing_stage} —— 新增人物时需补一行")

    missing_code = [s for s in slugs if s not in CODE_MAP]
    if missing_code:
        raise SystemExit(f"[CODE MISSING] CODE_MAP 未登记：{missing_code} —— 新增人物时需补一行")

    invalid = [(s, c) for s, c in CODE_MAP.items()
               if not (isinstance(c, str) and 2 <= len(c) <= 3 and c.isupper() and c.isalpha())]
    if invalid:
        raise SystemExit(f"[CODE INVALID] 短代码必须是 2–3 位大写字母（如 GS / HOM）：{invalid}")

    dup = [c for c, n in Counter(CODE_MAP.values()).items() if n > 1]
    if dup:
        raise SystemExit(f"[CODE COLLISION] 短代码冲突：{dup} —— 请修改 CODE_MAP 后重试")

    orphan = [s for s in CODE_MAP if s not in slugs]
    if orphan:
        raise SystemExit(f"[CODE ORPHAN] CODE_MAP 含不存在的人物：{orphan}")

    return len(slugs)

def update_registry():
    d = json.load(open(REG, encoding="utf-8"))
    existing = {s["name"] for s in d["skills"]}
    added = 0
    for p in PEOPLE:
        if p["name"] in existing:
            continue
        d["skills"].append({
            "name": p["name"], "person": p["person"], "domain": p["domain"],
            "domain_cn": p["domain_cn"], "region": p["region"], "status": "released",
            "code": CODE_MAP.get(p["name"], ""),
            "living": p.get("living"), "died": p.get("died"),
            "sources": p.get("sources") or [],
            "frameworks": p["frameworks"], "style_keywords": p["style_keywords"],
            "roundtable_role": p["roundtable_role"], "roundtable_tags": p["roundtable_tags"],
            "complements": p["complements"], "path": f"skills/{p['name']}"
        })
        added += 1
    # 回填 code / living / died / sources：即便已存在的 skill 也确保字段与 people.py 同步
    people_by_slug = {p["name"]: p for p in PEOPLE}
    for s in d["skills"]:
        s["code"] = CODE_MAP.get(s["name"], "")
        p = people_by_slug.get(s["name"])
        if p:
            s["living"] = p.get("living")
            s["died"] = p.get("died")
            s["sources"] = p.get("sources") or []
    d["version"] = REPO_VERSION
    d["updated"] = REPO_UPDATED
    json.dump(d, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return added, len(d["skills"])

def rebuild_matrix():
    d = json.load(open(REG, encoding="utf-8"))
    # 冲突检测：短代码必须唯一，否则构建即报错（防止 JS/JM 类静默冲突再次发生）
    _codes = list(CODE_MAP.values())
    if len(_codes) != len(set(_codes)):
        from collections import Counter
        _dup = [c for c, n in Counter(_codes).items() if n > 1]
        raise SystemExit(f"[CODE COLLISION] 短代码冲突：{_dup} —— 请修改 CODE_MAP 后重试")
    code_map, stage_map = CODE_MAP, STAGE_MAP
    experts = {}; tag_index = {}; stages = {"宏观定调":[], "中观筛选":[], "微观决策":[]}
    for s in d["skills"]:
        slug = s["name"]
        code = code_map.get(slug, "")
        # slug 是主键；code 仅为展示别名，存入对象便于 assemble 显示
        experts[slug] = {"code": code, "person": s["person"], "role": s["roundtable_role"],
                         "tags": s["roundtable_tags"], "stage": stage_map[slug], "path": s["path"]}
        for t in s["roundtable_tags"]:
            tag_index.setdefault(t, []).append(slug)
        stages[stage_map[slug]].append(slug)
    matrix = {"version": REPO_VERSION, "updated": REPO_UPDATED, "alias_map": code_map,
              "stages":stages,"experts":experts,"tag_index":tag_index}
    json.dump(matrix, open(MAT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(d["skills"]), len(experts), len(tag_index)

# ---------- main ----------

def main():
    total = 0
    validate_maps()  # 先守卫再写盘，避免写到一半才发现映射表缺人
    for p in PEOPLE:
        base = os.path.join(SKILLS, p["name"])
        w(os.path.join(base, "SKILL.md"), render_skill_md(p))
        w(os.path.join(base, "SKILL-condensed.md"), render_condensed(p))
        w(os.path.join(base, "PROFILE.md"), render_profile(p))
        w(os.path.join(base, "CITATION.cff"), render_citation(p))
        w(os.path.join(base, "CHANGELOG.md"), render_changelog(p))
        w(os.path.join(base, "examples", "INDEX.md"), render_examples_index(p))
        w(os.path.join(base, "references", "01-core-theories.md"), render_ref01(p))
        w(os.path.join(base, "references", "02-analysis-frameworks.md"), render_ref02(p))
        w(os.path.join(base, "references", "03-style-and-voice.md"), render_ref03(p))
        w(os.path.join(base, "references", "04-key-views-timeline.md"), render_ref04(p))
        w(os.path.join(base, "references", "05-publications.md"), render_ref05(p))
        w(os.path.join(base, "references", "06-glossary.md"), render_ref06(p))
        w(os.path.join(base, "references", "07-checklist.md"), render_ref07(p))
        w(os.path.join(base, "references", "08-style-anti-patterns.md"), render_ref08(p))
        total += 1
        print(f"  [ok] {p['person']} ({p['name']}) 14 files")
    added, reg_total = update_registry()
    m_total, m_exp, m_tag = rebuild_matrix()
    print(f"\n生成 skill: {total}")
    print(f"registry: +{added} → 共 {reg_total} 人 (v{REPO_VERSION})")
    print(f"matrix: {m_exp} 专家 / {m_tag} 标签")

if __name__ == "__main__":
    main()
