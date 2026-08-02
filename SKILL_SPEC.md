# SKILL 编写规范

本规范定义 SKILL Palace 中每个名人 skill 的标准结构与验收标准。质量基准参照 [gaoshanwen-skill](https://github.com/kevin12369/gaoshanwen-skill) v1.3.0 的生产级实践。

---

## 1. 目录结构

每位名人的 skill 是一个独立目录，位于 `skills/` 下：

```
skills/<name>/
├── SKILL.md                     # [必需] 主文件（完整版）
├── SKILL-condensed.md           # [推荐] 精简版变体（~5KB，省 token）
├── SKILL-<专项>.md              # [可选] 专项变体（如 a-share / real-estate）
├── SKILL.en.md                  # [可选] 英文版变体
├── PROFILE.md                   # [必需] 人物档案卡
│
├── references/                  # [必需] 编号化参考文件体系
│   ├── 01-core-theories.md      #   核心理论/思维模型详解
│   ├── 02-analysis-frameworks.md #  框架应用工作流
│   ├── 03-style-and-voice.md    #   表达风格与典型语录
│   ├── 04-key-views-timeline.md #   关键观点年表
│   ├── 05-publications.md       #   代表作索引
│   ├── 06-glossary.md           #   术语表
│   ├── 07-checklist.md          #   风格校准 checklist（正向）
│   └── 08-style-anti-patterns.md #  风格反例库（反向）
│
├── examples/                    # [推荐] 示例输出
│   ├── INDEX.md                 #   分类索引
│   ├── 01-<topic>.md            #   框架应用示例
│   ├── 02-<topic>.md            #   风格校准示例
│   └── ...
│
├── CITATION.cff                 # [推荐] 学术引用格式
└── CHANGELOG.md                 # [推荐] 版本历史
```

### 命名规则

- 目录名使用 **kebab-case**（如 `charlie-munger`、`gao-shanwen`）
- 目录名必须与 `SKILL.md` frontmatter 的 `name` 字段完全一致
- references/ 文件使用 **两位数字前缀**（`01-` 到 `08-`），确保加载顺序明确
- examples/ 文件使用 **两位数字前缀** + 主题描述

---

## 2. SKILL.md frontmatter

```yaml
---
name: <kebab-case-name>
description: <一段完整的描述，必须包含以下要素>
agent_created: true
---
```

### description 字段要求

`description` 是 Agent 决定何时加载该 skill 的唯一依据，必须包含：

1. **定位说明**：以谁的框架做什么类型的分析
2. **触发场景**：用户说什么话时应该激活
3. **关键词清单**：列出核心框架名称和触发词
4. **问题示例**：用户可能问的具体问题
5. **互补声明**：与其他 skill 的关系
6. **免责声明**：一句话声明不声称代表本人

### 示例

```yaml
description: 以查理·芒格的思维模型与投资哲学框架，对投资决策、商业判断、
企业质量评估与认知偏误检查做深度分析。当用户的请求命中以下场景时使用本技能：
要求"用芒格的框架分析""像芒格那样想想""芒格会怎么看""用多元思维模型"
"逆向思考一下""能力圈检验""Lollapalooza 效应""人类误判心理学"；
或用户希望得到带有犀利直白、逆向先行、跨学科视角、警句式表达的决策审视；
或用户提出"这笔投资该不该做""我是不是在能力圈外"等问题并希望以芒格视角研判。
本技能提供思维框架与文风，不声称代表芒格本人或其未公开观点。与聚焦中国宏观的
gao-shanwen、聚焦全球宏观的 greenspan 互补，本技能聚焦微观决策与商业判断。
```

---

## 3. SKILL.md 正文结构

SKILL.md 正文必须包含以下区块（按顺序）：

1. **标题**——`# <人物>思维框架与分析风格`
2. **目的**——为什么固化这个人物的框架，3-5 条要点
3. **定位声明（必须）**——"不声称代表本人"的显式声明
4. **何时使用**——触发场景 + 何时不使用（路由规则）
5. **核心思维模型**——至少 5 个，每个简要说明。指示"分析前调用 `references/01-core-theories.md`"
6. **工作流**——至少 5 步。指示"详细步骤见 `references/02-analysis-frameworks.md`"
7. **文风规范**——具体可执行。指示"完整规范见 `references/03-style-and-voice.md`"
8. **输出模板**——结构化的段落结构
9. **协作声明**——与其他 skill 的互补关系与路由规则

---

## 4. SKILL 变体机制

每个 skill 支持多个变体，按需选用。安装时将所需变体重命名为 `SKILL.md` 即可。

| 变体 | 文件名 | 大小 | 适用场景 |
|------|--------|------|---------|
| 完整版 | `SKILL.md` | 完整 | 深度分析，全量框架与文风 |
| 精简版 | `SKILL-condensed.md` | ~5KB | token 预算有限，快速调用 |
| 专项版 | `SKILL-<topic>.md` | - | 特定领域专项（如 A 股 / 房地产） |
| 英文版 | `SKILL.en.md` | - | 国际化场景 |

### 变体编写要求

- 所有变体共享同一 `name` 和触发词（frontmatter description）
- 精简版保留核心框架速览 + 文风要点 + 输出格式 + 合规声明
- 专项版聚焦特定领域，可省略不相关框架
- 英文版翻译完整版，保留文风 DNA（可能需要调整比喻的跨文化表达）

---

## 5. references/ 编号文件体系

references/ 从单个文件升级为 **8 个标准化编号文件**，实现渐进式精细加载：

| 文件 | 内容 | 何时加载 |
|------|------|---------|
| `01-core-theories.md` | 核心理论/思维模型详解（定义+场景+步骤+示例+注意事项） | 深度分析时 |
| `02-analysis-frameworks.md` | 框架应用工作流（从问题输入到结论输出的完整流程+分支路径） | 执行分析时 |
| `03-style-and-voice.md` | 表达风格 DNA（语气+句式+招牌比喻+典型语录+禁忌+正反示例） | 输出校准时 |
| `04-key-views-timeline.md` | 关键观点年表（不同时期的核心观点+立场变化记录） | 需要历史校准时 |
| `05-publications.md` | 代表作索引（著作/演讲/文章+框架提炼来源） | 知识溯源时 |
| `06-glossary.md` | 术语表（专有概念定义+人物专属表述+易混淆辨析） | 用词校准时 |
| `07-checklist.md` | 风格校准 checklist（正向：什么像） | **每次输出前必须** |
| `08-style-anti-patterns.md` | 风格反例库（反向：什么不像+错误示例+正确改写） | 输出校准时 |

### 正反双校验体系（核心创新）

`07-checklist.md`（正向）+ `08-style-anti-patterns.md`（反向）组成**正反双校验**：

- **正向**：输出前逐项检查"是否像 <人物>"（内容/风格/合规三维度）
- **反向**：检查"是否犯了常见偏差"（每个反例含错误输出+原因分析+正确改写）

这是 gaoshanwen-skill 的核心创新，极大提高 AI 模拟保真度。所有 skill 必须实现此双校验体系。

---

## 6. PROFILE.md 规范

每个 skill 必须包含 `PROFILE.md`，结构见 `_template/PROFILE.md`。

---

## 7. examples/ 规范

- 必须包含 `INDEX.md` 分类索引
- 至少 3 个示例：框架应用示例 + 风格校准示例 + 专项场景示例
- 每个示例包含：输入 + 框架选择 + 完整输出 + 校准说明

---

## 8. 治理文件

| 文件 | 用途 | 必需性 |
|------|------|--------|
| `CITATION.cff` | 学术引用格式（CFF 1.2.0） | 推荐 |
| `CHANGELOG.md` | 版本历史 | 推荐 |
| `LICENSE` | 开源协议（MIT） | 必需（仓库根目录） |
| `CONTRIBUTING.md` | 贡献指南 | 必需（仓库根目录） |
| `CODE_OF_CONDUCT.md` | 行为准则 | 推荐（仓库根目录） |
| `SECURITY.md` | 安全策略 | 推荐（仓库根目录） |
| `FAQ.md` | 常见问题 | 推荐 |

---

## 9. 验收清单

创建新 skill 时，提交前逐项检查：

### frontmatter
- [ ] `name` 与目录名一致（kebab-case）
- [ ] `description` 包含触发词、场景、互补关系、免责声明
- [ ] `agent_created: true` 存在

### SKILL.md 正文
- [ ] 含"目的"区块
- [ ] 含"不声称代表本人"的定位声明
- [ ] 核心思维模型至少 5 个
- [ ] 工作流至少 5 步
- [ ] 文风规范具体可执行
- [ ] 输出模板结构化
- [ ] 协作声明含路由规则

### references/ 编号文件（8 个全齐）
- [ ] `01-core-theories.md`：至少 5 个理论，每个含定义+场景+步骤+示例+注意事项
- [ ] `02-analysis-frameworks.md`：完整工作流 + 分支路径
- [ ] `03-style-and-voice.md`：语气+句式+招牌比喻+典型语录+禁忌+正反示例
- [ ] `04-key-views-timeline.md`：年表 + 立场变化记录
- [ ] `05-publications.md`：代表作索引 + 框架来源声明
- [ ] `06-glossary.md`：术语定义 + 专属表述 + 易混淆辨析
- [ ] `07-checklist.md`：内容+风格+合规三维度校验项
- [ ] `08-style-anti-patterns.md`：至少 4 个反例，每个含错误输出+原因+正确改写

### 变体（推荐）
- [ ] `SKILL-condensed.md` 精简版存在
- [ ] 专项变体（如有领域细分）

### 配套文件
- [ ] `PROFILE.md` 存在且含所有必需区块
- [ ] `examples/INDEX.md` 分类索引存在
- [ ] `examples/` 至少 3 个示例
- [ ] `CITATION.cff` 存在（推荐）
- [ ] `CHANGELOG.md` 存在（推荐）

### 质量检查
- [ ] 无占位符或 TODO
- [ ] 正反双校验体系完整（07 + 08）
- [ ] 互补关系与 `registry/index.json` 一致
- [ ] 不包含敏感或争议性内容
- [ ] 如人物已故，含致敬与伦理声明
