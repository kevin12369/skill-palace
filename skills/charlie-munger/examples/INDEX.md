# 示例索引

> 本目录用于存放 查理·芒格 skill 的示例输出：给用户看预期效果，给 Agent 校准风格。

## 当前状态

本目录当前有 **3 个**示例正文（由构建脚本扫描目录得出）：

| 文件 | 大小 |
|------|------|
| [example-01-inversion.md](example-01-inversion.md) | 3193 B |
| [example-02-latticework.md](example-02-latticework.md) | 2943 B |
| [example-03-three-baskets.md](example-03-three-baskets.md) | 3078 B |

## 选题参考（历史规划；某条是否已落地，以上表实际文件为准）

- **逆向思考应用** —— 用逆向思考评估商业模式的失败风险
- **多元模型格栅** —— 用3学科模型交叉验证一个投资判断

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
