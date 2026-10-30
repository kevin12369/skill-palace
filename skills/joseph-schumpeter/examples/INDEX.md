# 示例索引

> 本目录用于存放 约瑟夫·熊彼特 skill 的示例输出：给用户看预期效果，给 Agent 校准风格。

## 当前状态

本目录当前有 **3 个**示例正文（由构建脚本扫描目录得出）：

| 文件 | 大小 |
|------|------|
| [example-01-creative-destruction.md](example-01-creative-destruction.md) | 3334 B |
| [example-02-innovation-cluster.md](example-02-innovation-cluster.md) | 3367 B |
| [example-03-anti-pattern.md](example-03-anti-pattern.md) | 2277 B |

## 选题参考（历史规划；某条是否已落地，以上表实际文件为准）

- **创造性破坏扫描** —— 识别哪些行业正在经历范式级创新冲击
- **创新集群判断** —— 判断当前是否处于创新集群爆发期

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
