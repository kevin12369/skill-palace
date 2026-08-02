# 常见问题

## 通用问题

### SKILL Palace 和"人形 Skill"（同事/老板/前任 skill）有什么区别？

人形 Skill 追求"像那个人在跟你聊天"的沉浸感，偏娱乐。SKILL Palace 走相反路线：**不追求"像他"，而追求"用他的方法想问题"**。每个 skill 是思维框架与文风的工具，不是人格替身。且这些工具可以组合成"智囊团"实现多视角交叉验证。

### 这些 skill 会冒充名人本人吗？

不会。每个 skill 都显式声明"不声称代表本人"，输出中用"按 <人物> 框架分析"而非"<人物> 认为"。这是思维框架的工具化，不是人格复制。

### 安装后如何触发？

安装后无需手动注册。Agent 会根据 SKILL.md 中 `description` 字段的触发词自动激活。例如说"用芒格的框架分析一下"，Agent 即加载 charlie-munger skill。

## 安装与使用

### 完整版和精简版有什么区别？该装哪个？

| 变体 | 大小 | 适用场景 |
|------|------|---------|
| 完整版（SKILL.md） | 完整 | 深度分析，全量框架 |
| 精简版（SKILL-condensed.md） | ~5KB | token 预算有限，快速调用 |

建议默认装完整版。token 紧张时切换精简版：将 `SKILL-condensed.md` 重命名为 `SKILL.md` 即可。

### 支持哪些平台？

| 平台 | 安装路径 |
|------|---------|
| WorkBuddy | `~/.workbuddy/skills/<name>/` |
| Claude Code | `.claude/skills/<name>/` |
| Cursor | `.cursor/skills/<name>/` |
| OpenClaw | `~/.openclaw/skills/<name>/` |
| Codex | `$CODEX_HOME/skills/` |
| Trae | `.trae/skills/` |
| 其他 agentskills.io 兼容平台 | 对应 skills 目录 |

### 如何使用智囊团组合？

参见 [combos/](combos/) 目录。每个 combo 文件定义了多 skill 会诊的协作流程。在对话中说明需要多视角分析即可触发，如"用高善文和格林斯潘的框架一起分析"。

## 贡献

### 如何提名一位新名人？

使用 [Issue 模板](.github/ISSUE_TEMPLATE/request-persona.md) 提交提名。需说明人物信息、可复用的思维框架、公开材料来源、文风特征、互补关系。

### 如何创建新 skill？

复制 `skills/_template/` 目录，遵循 [SKILL_SPEC.md](SKILL_SPEC.md) 规范。重点：8 个编号 references 文件全齐、正反双校验体系（07+08）完整。

### 为什么需要 8 个 references 文件而不是 1 个？

实现渐进式精细加载——Agent 按需加载最相关的参考文件，而非一次性加载全部。同时，`07-checklist.md`（正向校验）+ `08-style-anti-patterns.md`（反向校验）组成的正反双校验体系能极大提高 AI 模拟保真度。
