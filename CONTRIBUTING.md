# 贡献指南

感谢你对 SKILL Palace 的兴趣！本指南说明如何提名新名人、创建新 skill 或提交智囊团组合。

---

## 贡献方式

| 方式 | 适合谁 | 如何开始 |
|------|--------|---------|
| 提名一位名人 | 所有用户 | 提交 [Issue](.github/ISSUE_TEMPLATE/request-persona.md) |
| 创建新 skill | 开发者 | 复制 `skills/_template/`，遵循 [SKILL_SPEC.md](SKILL_SPEC.md) |
| 提交智囊团组合 | 开发者 | 在 `combos/` 下新建 `.md` 文件 |
| 改进现有 skill | 开发者 | 直接提交 PR |
| 反馈与建议 | 所有用户 | 提交 Issue |

---

## 创建新 skill 的流程

### 第 1 步：确认人物适合收录

SKILL Palace 收录的人物需满足：

- **世界知名**：在某个领域有公认的影响力与代表性
- **有可复用的思维框架**：不是"会聊天的人设"，而是有结构化的分析方法论
- **有充足的公开材料**：框架可从公开著作/演讲/文章中提炼
- **无伦理争议**：不涉及敏感政治人物；在世人物需特别注意免责声明

### 第 2 步：提交提名 Issue（可选但推荐）

先提交 Issue 说明你打算创建哪个 skill，避免与他人重复。

### 第 3 步：复制模板开始

```bash
cp -r skills/_template skills/<your-skill-name>
```

### 第 4 步：编写 SKILL.md

遵循 [SKILL_SPEC.md](SKILL_SPEC.md) 的规范，逐区块填写。重点：

- `description` 必须包含触发词、场景、互补关系、免责声明
- 核心思维模型至少 5 个
- 工作流至少 5 步
- 文风规范要有正反示例

### 第 5 步：编写 PROFILE.md

填写人物档案卡的所有必需区块，特别注意"框架来源声明"和"免责声明"。

### 第 6 步：编写 references/frameworks.md

将核心思维模型详细展开，每个模型包含定义、适用场景、操作步骤、示例、注意事项。

### 第 7 步：编写 examples/sample-output.md

提供一份完整的分析输出样本，让用户预期 skill 的效果。

### 第 8 步：更新 registry/index.json

在 `skills` 数组中添加你的 skill 条目，包含 name、person、domain、frameworks、complements 等字段。

### 第 9 步：更新 README.md

在"名人堂成员总览"表格和"按领域浏览"中添加你的 skill。

### 第 10 步：验收检查

对照 [SKILL_SPEC.md 的验收清单](SKILL_SPEC.md#6-验收清单) 逐项检查，然后提交 PR。

---

## 创建智囊团组合

在 `combos/` 下新建 `.md` 文件，包含：

- 组合名称与成员
- 适用场景
- 协作流程（各 skill 的调用顺序与交叉验证逻辑）
- 互补逻辑说明
- 输出格式

参考 [combos/macro-council.md](combos/macro-council.md)。

---

## 代码规范

- 目录名使用 kebab-case
- Markdown 文件使用 UTF-8 编码
- frontmatter 使用合法 YAML
- 不包含敏感信息、个人隐私或争议性内容
- 每个 skill 必须有"不声称代表本人"的免责声明

---

## PR 流程

1. Fork 仓库
2. 创建分支：`git checkout -b skill/<name>` 或 `git checkout -b combo/<name>`
3. 提交改动
4. 确保 CI 检查通过（自动校验 frontmatter、目录结构）
5. 提交 PR，描述你新增/改进的内容

维护者会在收到 PR 后尽快 review。

---

## 行为准则

- 尊重每位被收录的人物——skill 是对其思维框架的致敬，不是嘲弄
- 尊重其他贡献者
- 聚焦"思维工具"的价值，而非"模仿本人"的娱乐性
