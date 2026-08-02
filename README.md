# SKILL Palace

> 世界知名人物思维框架的 SKILL 化名人堂——将各领域顶尖人物的分析方法论、决策框架与表达风格，固化为 Agent 可即装即用的可复用技能。

![License](https://img.shields.io/badge/license-MIT-blue)
![Skills](https://img.shields.io/badge/skills-3%20released-green)
![Platform](https://img.shields.io/badge/platform-WorkBuddy%20%7C%20Claude%20Code-purple)

---

## 什么是 SKILL Palace

SKILL Palace 不是"人设聊天机器人"。它走的是相反路线：**不追求"像他"，而追求"用他的方法想问题"**。

- 别人做"赛博朋友圈"（像谁在跟你聊天）
- SKILL Palace 做"思维工具箱"（用谁的方法论分析问题）
- 且这些工具可以**组合成智囊团**，多视角交叉验证

每个 skill 都是**思维框架与文风的工具**，用于辅助用户自行研判。它不声称代表人物本人，也不引用任何未公开的专有研究。

---

## 名人堂成员总览

| 人物 | 领域 | 核心框架 | 文风关键词 | 状态 | 安装命令 |
|------|------|---------|-----------|------|---------|
| 高善文 | 宏观经济 | 资产重估理论、河床水位比喻、刘易斯拐点 | 隐喻化、方法论先行、长期视角 | ✅ 已发布 | `cp -r skills/gao-shanwen ~/.workbuddy/skills/` |
| 格林斯潘 | 全球宏观 | Fedspeak、全球储蓄过剩、非理性繁荣 | 数据驱动、谨慎含蓄、多层语义 | ✅ 已发布 | `cp -r skills/greenspan ~/.workbuddy/skills/` |
| 查理·芒格 | 投资决策 | 多元思维模型、逆向思考、Lollapalooza 效应 | 犀利直白、警句式、承认无知 | ✅ 已发布 | `cp -r skills/charlie-munger ~/.workbuddy/skills/` |

---

## 按领域浏览

### 宏观经济

<details>
<summary><b>宏观经济（2 个 skill）</b></summary>

#### 高善文 — 中国宏观经济

- **框架**：资产重估理论、河床水位比喻、刘易斯拐点/人口结构
- **文风**：隐喻化、方法论先行、长期视角
- **触发词**："用高善文的框架分析""像高善文那样讲讲""资产重估理论""河床水位"
- **互补**：与格林斯潘（全球宏观）互补，覆盖中国 vs 全球
- **详情**：[→ skills/gao-shanwen](skills/gao-shanwen)

#### 格林斯潘 — 全球宏观与美联储

- **框架**：Fedspeak、全球储蓄过剩、利率之谜、生产率奇迹、非理性繁荣
- **文风**：数据驱动、谨慎含蓄、多层语义、长期视角
- **触发词**："用格林斯潘的框架分析""Fedspeak""非理性繁荣""Greenspan Put"
- **互补**：与高善文（中国宏观）互补，覆盖全球 vs 中国
- **详情**：[→ skills/greenspan](skills/greenspan)

</details>

### 价值投资与决策

<details>
<summary><b>价值投资与决策（1 个 skill）</b></summary>

#### 查理·芒格 — 微观决策与商业判断

- **框架**：多元思维模型格栅、逆向思考、能力圈、安全边际、Lollapalooza 效应、人类误判心理学 25 条、三筐分类法
- **文风**：犀利直白、逆向先行、警句式、承认无知
- **触发词**："用芒格的框架分析""逆向思考""能力圈""Lollapalooza""人类误判心理学"
- **互补**：与高善文、格林斯潘形成三层互补——宏观（中国/全球）+ 微观决策
- **详情**：[→ skills/charlie-munger](skills/charlie-munger)

</details>

---

## 智囊团组合

SKILL Palace 的 skill 不是孤立的——它们可以组合成"多人物会诊"方案，实现多视角交叉验证。

| 组合名 | 成员 | 适用场景 | 文档 |
|--------|------|---------|------|
| 宏观智囊团 | 高善文 + 格林斯潘 | 需要同时看中国宏观与全球宏观（中美利差、全球资本流动） | [→ combos/macro-council](combos/macro-council.md) |
| 三层互补 | 高善文 + 格林斯潘 + 芒格 | 从宏观到微观的完整分析链 | 规划中 |

### 互补关系图谱

```
高善文（中国宏观）── 互补 ── 格林斯潘（全球宏观）
                                    │
                                 互补
                                    │
                              芒格（微观决策）
```

- **高善文 × 格林斯潘**：全球流动性是中国资产定价的外生变量，两者覆盖"全球水位"与"中国河床"
- **格林斯潘 × 芒格**：宏观环境是微观决策的背景，芒格的逆向思考可检验宏观叙事的盲点
- **高善文 × 芒格**：中国宏观判断 + 微观决策审视，覆盖"看对大势"与"做对决策"

---

## 快速开始

### 安装单个 skill

```bash
# 1. 克隆仓库
git clone https://github.com/<your-user>/skill-palace /tmp/skill-palace

# 2. 复制你需要的 skill（以 charlie-munger 为例）

# 方式一：用户级安装（推荐，所有项目可用）
cp -r /tmp/skill-palace/skills/charlie-munger ~/.workbuddy/skills/charlie-munger

# 方式二：项目级安装（仅当前项目）
cp -r /tmp/skill-palace/skills/charlie-munger your-project/.workbuddy/skills/charlie-munger

# 方式三：Claude Code 兼容安装
cp -r /tmp/skill-palace/skills/charlie-munger your-project/.claude/skills/charlie-munger
```

### 安装全部 skill

```bash
cp -r /tmp/skill-palace/skills/* ~/.workbuddy/skills/
```

### 选择 SKILL 变体

每个 skill 支持多个变体，按需选用。安装时将所需变体重命名为 `SKILL.md` 即可：

| 变体 | 文件名 | 适用场景 |
|------|--------|---------|
| 完整版（默认） | `SKILL.md` | 深度分析，全量框架与文风 |
| 精简版 | `SKILL-condensed.md` | token 预算有限，快速调用（~5KB） |
| 专项版 | `SKILL-<topic>.md` | 特定领域专项（如 A 股 / 房地产） |
| 英文版 | `SKILL.en.md` | 国际化场景 |

```bash
# 示例：安装精简版
cp /tmp/skill-palace/skills/charlie-munger/SKILL-condensed.md ~/.workbuddy/skills/charlie-munger/SKILL.md
```

### 验证

安装后，在对话中输入触发词，Agent 应自动加载该 skill：

> "用芒格的框架分析一下这笔投资该不该做"
> "像高善文那样讲讲当前的市场"

若未自动触发，检查 `SKILL.md` 的 `description` 字段是否包含对应关键词。无需手动注册——Agent 会根据 description 中的触发词自动激活。

---

## 贡献

欢迎提名新名人或贡献新 skill！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

- **提名一位名人**：使用 [Issue 模板](.github/ISSUE_TEMPLATE/request-persona.md) 提交提名
- **创建新 skill**：复制 `skills/_template/` 目录开始，遵循 [SKILL_SPEC.md](SKILL_SPEC.md) 规范
- **提交智囊团组合**：在 `combos/` 下新建组合方案文件

---

## 兼容性

| 平台 | 安装路径 | 状态 |
|------|---------|------|
| WorkBuddy | `~/.workbuddy/skills/<name>/` | ✅ 完全兼容 |
| Claude Code | `.claude/skills/<name>/` | ✅ 兼容 |
| Cursor | `.cursor/skills/<name>/` | ✅ 兼容 |
| OpenClaw | `~/.openclaw/skills/<name>/` | ✅ 兼容 |
| Codex | `$CODEX_HOME/skills/` | ✅ 兼容 |
| Trae | `.trae/skills/` | ✅ 兼容 |
| 其他 agentskills.io 兼容平台 | 对应 skills 目录 | ✅ 兼容 |

---

## 设计文档

- [SKILL 编写规范](SKILL_SPEC.md)——frontmatter、结构、验收标准
- [设计哲学](docs/philosophy.md)——为什么是"框架"而非"替身"
- [智囊团组合指南](docs/combination-guide.md)——如何使用和创建组合
- [机器可读索引](registry/index.json)——程序化发现与安装

## License

MIT
