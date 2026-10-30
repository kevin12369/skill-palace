# SKILL Palace 仓库体检报告（P0 · 只读审计）

> 审计对象：`kevin12369/skill-palace` @ `main`
> 审计 commit：`1dc94ccc25dff8d9dccbdff0f317397b5f05e461`（2026-08-07 18:04:52 +0800，`feat: add 威廉·欧奈尔 ... (v2.7.0, 50→51 people)`）
> 本地副本与远端一致性：`git rev-list --left-right --count HEAD...origin/main` → `0	0`（完全同步）
> 审计方式：只读。本报告为唯一新增文件，未修改任何已有文件（`git status --short` 除本文件外为空）。
> 审计日期：2026-10-30

> **本报告是 `1dc94cc` 这个时间点的快照，不作为当前状态引用。** 其中列出的主要问题随后续提交
> 已处理，当前状态请以两个脚本的实测输出为准：
>
> | 本报告的条目 | 当前状态 |
> |---|---|
> | B-1「示例文件 0 个、索引 102 条幻影引用」 | 已解决：`build.py` 补写至每 skill 3 篇，全库 153 篇，INDEX 改为按目录扫描生成 |
> | §7「至少 3 个示例」全库违规 | 已解决：audit 的 EX-02 通过，51/51 |
> | 15 个 skill 的 `01-core-theories.md` 理论块 < 5 | 已解决：补写 39 个理论块，theories 分布 `{5: 16, 6: 35}` |
> | 协作声明模板化（未逐条点名 complements） | 已解决：`build.py` 的 `collab_block()` 逐条点名，QL-03 通过 |
> | CI 只查文件名与 frontmatter，绿灯 ≠ 符合 SPEC | 已解决：新增 `scripts/check_registry.py`（R01-R21）与 `scripts/audit_skills.py`（ERROR 0 ／ WARN 0） |
>
> 复核命令：`python scripts/check_registry.py && python scripts/audit_skills.py`。

### 关于字节数的一个口径说明

工作区字节数受 CRLF 影响，与 GitHub 上的真实大小不一致。本报告**一律使用 git blob 尺寸**：

```bash
git cat-file -s HEAD:README.md   # → 43719（与 GitHub raw 一致）
wc -c README.md                  # → 44404（工作区，CRLF 膨胀，不可用）
```

原因：`.gitattributes` 中 `*.md text eol=lf` 使提交内容为 LF，而 Windows 工作区检出/写入为 CRLF，每行多 1 字节。

---

## 一、CI 复现结果

CI 定义：`.github/workflows/lint-skills.yml`（4818 字节），仅一个 `lint` job，核心是一个 Python 内联脚本，校验 6 类事项。

**复现方法**：CI 是在干净 checkout 上运行的，看不到本地未跟踪的残留目录。为忠实复现，用 `git archive HEAD` 导出纯净树后再跑 workflow 中的原始脚本：

```bash
git archive HEAD | tar -x -C /tmp/sp-audit
cd /tmp/sp-audit && python _audit_ci.py     # 脚本逐字复制自 lint-skills.yml
```

**结果：全部通过。**

```
exit code = 0
[OK] 行数     = 51
WARN 行数     = 0
ERROR 行数    = 0
末尾输出      = All skills passed validation.
```

51 个 skill 逐个输出 `[OK]`，无一条 `WARN`（即全部具备 `SKILL-condensed.md`），无一条 `ERROR`。

**CI 实际覆盖了哪些、没覆盖哪些**（这一节比"通过"本身更重要）：

| CI 检查项 | 是否覆盖 | 说明 |
| --- | --- | --- |
| `SKILL.md` 存在 | ✅ | 缺则记 error |
| frontmatter 含 `name:` `description:` `agent_created:` | ✅ | 仅检查**字符串存在**，不校验值 |
| `name` 与目录名一致 | ✅ | 精确匹配 |
| 免责声明含"不声称" | ✅ | 子串匹配 |
| `PROFILE.md` 存在 | ✅ | — |
| `references/` 下 8 个固定文件名 | ✅ | 只查**文件名**，不查内容 |
| `examples/INDEX.md` 存在 | ✅ | **只查 INDEX.md 本身，不查它引用的示例文件是否存在** |
| `SKILL-condensed.md` | ⚠️ 仅 WARN | 不阻断 |
| `SKILL_SPEC.md` §7「examples ≥3 个示例」 | ❌ 未覆盖 | 这是全仓 51/51 违规的地方（见第四节） |
| `SKILL_SPEC.md` §9「`08` 反例 ≥4 个」 | ❌ 未覆盖 | 15 个 skill 不达标 |
| `SKILL_SPEC.md` §8「LICENSE 必需」 | ❌ 未覆盖 | 仓库根本没有 LICENSE |
| `registry/index.json` ↔ `roundtable-matrix.json` 一致性 | ❌ 未覆盖 | 两者已出现漂移（见第四节 A-1） |
| `registry` 版本号与最新 tag/commit 一致 | ❌ 未覆盖 | 版本仍是 2.5.0 |
| README 与仓库实际数字一致 | ❌ 未覆盖 | 见第三节 |

> 结论：CI 是"文件名与 frontmatter 存在性"级别的门禁，绿灯**不代表**符合 `SKILL_SPEC.md`。这与 P0 的价值判断一致——需要通过体检而非 CI 来发现真实问题。

另外记录一个**未被 git 跟踪的本地残留**：工作区里存在空目录 `skills/skills/`（`.gitignore` 第 19 行专门屏蔽了它）。它不在 git 中，所以干净 checkout 的 CI 看不到；但只要有人误提交，CI 会把它当作名为 `skills` 的 skill 并因缺 `SKILL.md` 而报错。

```bash
ls -1d skills/*/ | wc -l                    # → 53（工作区，含残留 skills/skills）
git ls-tree -d --name-only HEAD skills/ | wc -l   # → 52（git 中，51 人物 + _template）
git ls-tree -d --name-only HEAD skills/skills      # → 空（未跟踪）
```

---

## 二、真实目录清单

统计口径（两个数字必须区分）：

```bash
git ls-tree -d --name-only HEAD skills/ | wc -l                            # → 52（git 跟踪的一级目录总数）
git ls-tree -d --name-only HEAD skills/ | grep -v '^skills/_template$' | wc -l   # → 51（真实人物目录）
```

- git 跟踪的一级目录：**52** = 51 位人物 + 1 个 `_template`
- 真实人物目录：**51**

### 2.1 结构一致性

对 51 个目录逐个检查（`for d in ...; do [ -f skills/$d/SKILL.md ] ...`），结果**高度一致，无一例外**：

| 目录名 | SKILL.md | PROFILE.md | references 份数 | examples 数 | CHANGELOG | CITATION.cff |
| --- | --- | --- | --- | --- | --- | --- |
| beijing-chaojia | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| ben-bernanke | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| burton-malkiel | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| carlota-perez | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| charles-ellis | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| charlie-munger | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| daniel-kahneman | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| duan-yongping | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| fred-schwed | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| fu-peng | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| gao-shanwen | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| gartner-hype-cycle | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| george-douglas-taylor | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| george-soros | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| greenspan | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| hong-hao | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| howard-marks | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| hyman-minsky | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| irving-fisher | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| james-simons | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| jeff-cooper | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| jesse-livermore | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| john-gordon | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| joseph-granville | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| joseph-schumpeter | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| junshan-jushi | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| kondratiev | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| larry-williams | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| li-daxiao | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| liu-shunren | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| long-qitian | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| martin-schwartz | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| michael-steinhardt | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| nassim-taleb | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| peter-lynch | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| philip-fisher | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| qin-guoan | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| qiu-guolu | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| ray-dalio | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| richard-wyckoff | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| robert-shiller | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| stanley-druckenmiller | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| theodore-wright | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| warren-buffett | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| william-gann | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| william-jevons | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| william-oneil | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| xu-wenming | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| xu-xiang | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| yang-jiyuan | ✅ | ✅ | 8 | 1 | ✅ | ✅ |
| yeshan-zhangwenhua | ✅ | ✅ | 8 | 1 | ✅ | ✅ |

> 「examples 数 = 1」指的是目录里只有 `examples/INDEX.md` 一个文件，**没有任何示例正文文件**。这不是本表的笔误，而是第四节 B-1 的核心问题。

### 2.2 registry 三方比对

```bash
python -c "import json;d=json.load(open('registry/index.json',encoding='utf-8'));print(len(d['skills']))"          # → 51
python -c "import json;d=json.load(open('registry/roundtable-matrix.json',encoding='utf-8'));print(len(d['experts']))" # → 51
```

| 口径 | 数量 | 差异 |
| --- | --- | --- |
| skills/ 真实人物目录 | 51 | — |
| registry/index.json `skills[]` | 51 | 无漏登、无幽灵条目 |
| registry/roundtable-matrix.json `experts` | 51 | 无漏登、无幽灵条目 |

三方集合完全相等（差集均为空）。**但内部字段有缺陷**，见第四节 A-1。

---

## 三、README 数字核对表

README.md 共 9 个 `##` 二级标题、27 个 `###` 三级标题、22 个 `<details>` 小节。逐项核对如下。

| # | README 声明的数字 | 位置 | 实测真值 | 计数命令 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 1 | 徽章 3 个 | 第 5–7 行 | 3 | `grep -c 'img.shields.io' README.md` → 3 | ✅ 一致 |
| 2 | `skills-51 released` | 第 6 行徽章 | 51 | 见第二节口径 | ✅ 一致 |
| 3 | 名人堂成员总览表 51 行 | 第 23–80 行 | 51 行数据、51 个 ✅ | `sed -n '23,80p' README.md \| grep -c '^\|'` → 53（减表头+分隔=51）；`grep -o '✅' \| wc -l` → 51 | ✅ 一致 |
| 4 | 按领域浏览：22 个 `<details>` | 第 81–526 行 | 22 | `grep -c '<details>' README.md` → 22 | ✅ 一致 |
| 5 | 按领域浏览：各小节声明数**合计** | 22 个 `<summary>` | **36** | 见下方明细 | ⚠️ 只覆盖 36/51 |
| 6 | 圆桌会议表「18 组」 | 第 531–551 行 | **19 组** | `sed -n '527,554p' README.md \| grep -c '^\|'` → 21（减 2 = 19） | ⚠️ 实测比基线多 1 |
| 7 | 专家角色表「37 行」 | 第 557–594 行 | **36 行** | `sed -n '555,597p' README.md \| grep -c '^\|'` → 38（减 2 = 36） | ⚠️ 实测比基线少 1 |
| 8 | 快速开始「7 个平台路径」 | 第 612–620 行 | **6 个平台** | 表内 6 行（WorkBuddy/Claude Code/Cursor/OpenClaw/Codex/Trae） | ⚠️ 实测 6 |
| 9 | 兼容性表 7 行 | 第 664–672 行 | 7 行 | 6 平台 + "其他 agentskills.io 兼容平台" | ✅ 一致 |
| 10 | 变体 4 种（完整/精简/专项/英文） | 第 630–635 行 | 实际只有 2 种落地 | `find skills -name 'SKILL.en.md' \| wc -l` → **0**；`find skills -maxdepth 2 -name 'SKILL-*.md'` → 仅 `SKILL-condensed.md` ×52 | ❌ 专项版/英文版无实物 |
| 11 | 设计文档 4 条链接 | 第 678–681 行 | 4 条，其中 **2 条死链** | `git ls-tree HEAD docs/` → 空；`ls docs/` → 空目录（且未跟踪） | ❌ 2 条死链 |
| 12 | License: MIT | 第 683–685 行 | 无 LICENSE 文件 | `ls LICENSE*` → No such file | ❌ 无实物 |
| 13 | 51 个 skill 各自"多个变体" | 第 626 行 | 平均只有 SKILL.md + SKILL-condensed.md | 同上 | ⚠️ 表述夸大 |

### 第 5 行明细（22 个小节各自声明的 skill 数）

```
宏观经济 2 / 价值投资与决策 2 / 技术周期 2 / 金融不稳定 1 / 宏观周期与债务 1
创新经济学 1 / 资源与技术 2 / 技术采纳 1 / 宏观对冲与反身性 1 / 货币经济学 1
成长股投资 2 / 行为金融与泡沫 2 / 有效市场与长期投资 2 / 风险与不确定性 2
中国价值与财务分析 3 / 金融史与市场文化 2 / 货币政策与危机 1 / 宏观策略与A股判断 3
短线交易与题材博弈 2 / 宏观投资与资本保全 1 / CAN SLIM选股系统 1 / 量化投资 1
```

合计 = 36。**"51 / 36 / 36" 三个数字同时出现在一份 README 里**，这是最容易被访客一眼看穿的矛盾。

---

## 四、问题清单

严重度含义：**阻断** = 对外可见的错误承诺或合规缺口；**重要** = 功能/一致性缺陷；**建议** = 可维护性问题。

### A. 注册表与构建链

| 编号 | 位置 | 问题描述 | 严重度 | 建议修法 | 需人工决策 |
| --- | --- | --- | --- | --- | --- |
| A-1 | `registry/roundtable-matrix.json`、`registry/index.json`、`tools/skill-gen/build.py:470` | **两名专家的 `code` 为空且缺 `alias_map` 条目**：`stanley-druckenmiller`、`william-oneil`。矩阵中 `experts` 有 51 个但 `alias_map` 只有 49 个。根因：`build.py` 的 `CODE_MAP` 只有 49 条，缺这两个 slug（而 `STAGE_MAP` 第 505–506 行**有**，所以 stage 字段是对的，只有 code 丢了）。`_codes` 冲突检测因空值重复而形同虚设。 | 🟠 重要 | 在 `CODE_MAP` 补两行（如 `"stanley-druckenmiller":"SD"`、`"william-oneil":"WO"`），重跑 `build.py`；同时把冲突检测改为忽略空值或显式报错空值 | 否（但短代码取值建议确认） |
| A-2 | `tools/skill-gen/build.py:528-529,552,582` | **版本常量硬编码且从未递增**：`d["version"]="2.5.0"`、`d["updated"]="2026-08-06"`、matrix `"version":"2.5"`。仓库已发到 v2.6.0、v2.7.0 两个 commit，但 registry 两个文件仍写 2.5.0。且 index 用三段的 `2.5.0`、matrix 用两段的 `2.5`，**格式本身不统一**。 | 🟠 重要 | 把版本号抽成单一常量，或从 `VERSION` 文件 / git tag 读取；index 与 matrix 统一为三段式 | 是（版本号以哪年为准需定口径） |
| A-3 | `combos/ROUNDTABLE.md:11`、`:291` | 两处仍写"**49 份**完整 SKILL.md"，实际 51 人 | 🟡 建议 | 改 49 → 51（或改为"全部 SKILL.md"以免再漂移） | 否 |

### B. 规范符合性（`SKILL_SPEC.md` 自身要求，CI 未覆盖）

| 编号 | 位置 | 问题描述 | 严重度 | 建议修法 | 需人工决策 |
| --- | --- | --- | --- | --- | --- |
| B-1 | `skills/*/examples/`（全部 51 个） | **示例文件 0 个，但索引声称 102 个**。全仓 `examples/` 除 `INDEX.md` 外无任何文件；51 个 `INDEX.md` 各自在表格里列出 2 个 `example-01-*.md` / `example-02-*.md`，逐个验证**全部不存在**（51×2 = 102 条幻影引用）。同时 `SKILL_SPEC.md` §7 要求「至少 3 个示例」，连"声称数"也只有 2。**减轻情节**：`INDEX.md` 末尾自注「Agent：运行时不加载本目录（仅供参考）」，故不影响运行时，属文档债。 | 🟠 重要 | **两条路选一**：(a) 补写示例（51×3 = 153 个文件，工作量大）；(b) 改写 `INDEX.md`，删除幻影表格、如实声明"示例待补"，并下调 §7 要求。推荐 (b) + 逐步补 5–8 个旗舰 skill | **是**（补写 vs 删链接，正是需要你定的那个决策） |
| B-2 | `skills/*/references/08-style-anti-patterns.md` | **15 个 skill 的反例数 < SPEC §9 要求的 4 个**。仅 1 个反例（11 个）：`gartner-hype-cycle` `george-soros` `greenspan` `hyman-minsky` `irving-fisher` `joseph-schumpeter` `kondratiev` `philip-fisher` `ray-dalio` `theodore-wright` `william-jevons`；仅 2 个（4 个）：`carlota-perez` `charlie-munger` `gao-shanwen` `warren-buffett`。其余 36 个达标（均为 4 个）。**值得注意的反常**：手工打磨的旗舰 skill（高善文、格林斯潘、芒格、巴菲特）反而不如批量生成的 36 个，说明生成器已具备 4 反例模板而这些早期文件未回填。 | 🟠 重要 | 优先回填这 15 个（尤其 4 个旗舰）；并把「反例 ≥4」加进 CI | 否 |
| B-3 | 仓库根目录 | **缺 LICENSE 文件**。`SKILL_SPEC.md` §8 明确把 `LICENSE` 标为「必需（仓库根目录）」，README 也宣称 MIT。CI 不检查此项，故长期漏网。 | 🔴 阻断 | 新增标准 MIT `LICENSE`。**注意**：不要照抄 gaoshanwen-skill 的 LICENSE（它在 MIT 正文里插入了致敬行，导致 GitHub 判 NOASSERTION，见附录 D-1） | **是**（著作权人署名写谁：个人 or "SKILL Palace contributors"） |
| B-4 | 51 个 `SKILL.md` | 其余可量化条款**全部达标**：核心思维模型 ≥5、工作流 ≥5 步、§3 九大区块齐全、`SKILL-condensed.md` 52/52 存在、无 TODO/占位符、已故人物致敬/伦理声明抽检 11 个全部具备 | ✅ 通过 | 无需修 | 否 |

### C. README 对外可见错误

| 编号 | 位置 | 问题描述 | 严重度 | 建议修法 | 需人工决策 |
| --- | --- | --- | --- | --- | --- |
| C-1 | `README.md:679-680` | **两处死链**：`docs/philosophy.md`、`docs/combination-guide.md`。git 中无 `docs/` 目录（`git ls-tree HEAD docs/` 为空）。 | 🔴 阻断 | **两条路选一**：(a) 补写两篇设计文档（推荐，正好可作为 `docs/` 起点）；(b) 改为指向 `SKILL_SPEC.md` / `combos/ROUNDTABLE.md` 中已存在的对应内容，或直接删掉这两条 | **是**（补写 vs 删链接） |
| C-2 | `README.md:6` 徽章、`:23-80` 总览表 vs `:81-526` 按领域浏览 vs `:557-594` 专家角色 | **同一份 README 内三个数字打架**：51 / 36 / 36。且**两张表漏掉的是同一批 15 人**（见下方 4.1 明细），说明这是"先按 36 人写 README，后又加了 15 人但没回填"的历史遗留，而非两处独立笔误。 | 🔴 阻断 | 补齐两张表到 51 人；或把徽章/总览表标注为"共 51 位，其中 36 位已完成领域分类"。推荐补全（15 人已在总览表里有完整信息，搬运成本不高） | 是（选补全还是选改口径） |
| C-3 | `README.md:630-635` | **变体宣称无实物**：表格列出"专项版 `SKILL-<topic>.md`"与"英文版 `SKILL.en.md`"，但全仓 `SKILL.en.md` = **0 个**、专项版 = **0 个**，只有 `SKILL-condensed.md` 落地（52 个）。 | 🟠 重要 | 在表格里注明"专项版/英文版为可选，目前仅 `gao-shanwen` 的独立仓库提供"；或去掉这两行 | 是（是否打算补齐） |
| C-4 | `README.md:683-685` | License 段写 `MIT`，但无 LICENSE 文件（同 B-3，此处为对外表述侧） | 🔴 阻断 | 与 B-3 一并解决 | 是 |
| C-5 | `README.md` 全文 | **`FAQ.md` 完全没有被链接**（`grep -n 'FAQ' README.md` → 无输出），2667 字节的 FAQ 成为孤儿文件 | 🟡 建议 | 在「贡献」或「快速开始」段加一条链接 | 否 |
| C-6 | `README.md:612-620` vs `:664-672` | 快速开始表列 **6** 个平台，兼容性表列 **7** 行（多"其他 agentskills.io 兼容平台"）。两表口径不一致 | 🟡 建议 | 统一：快速开始表也加"其他兼容平台"行，或兼容性表移除 | 否 |
| C-7 | `README.md:27` | 高善文那行的安装命令是 `git clone https://github.com/kevin12369/gaoshanwen-skill`，而其余 50 位都走本仓库路径。该独立仓库内容确实更完整（13 个 examples vs 本仓库 0 个），**但也意味着"51 位同构"的说法在这一行不成立** | 🟠 重要 | **两条路选一**：(a) 保留指向独立仓库，但加一句脚注说明"高善文另有独立仓库，内容更全"；(b) 改为与其他 50 位一致的本地路径 | **是** |

#### 4.1 「按领域浏览」与「专家角色表」共同漏掉的 15 位

```bash
# 按领域浏览：提取段内 skills/<slug> 链接去重
python -c "
import re,json
t=open('README.md',encoding='utf-8').read()
s=t[t.find('## 按领域浏览'):t.find('## 圆桌会议')]
print(len(set(re.findall(r'skills/([a-z0-9\-]+)\]',s))))"     # → 36
```

实测两张表覆盖的都是 **36 位**，缺的是**完全相同的 15 位**（专家角色表中"威廉·杰文斯"为"威廉·斯坦利·杰文斯"的简称，已覆盖，不算缺口）：

| # | slug | 人物 | 流派归类 |
| --- | --- | --- | --- |
| 1 | `jesse-livermore` | 杰西·利弗莫尔 | 技术分析/趋势交易 |
| 2 | `william-gann` | 威廉·江恩 | 技术分析 |
| 3 | `richard-wyckoff` | 理查德·威科夫 | 技术分析 |
| 4 | `joseph-granville` | 约瑟夫·格伦维尔 | 技术分析 |
| 5 | `martin-schwartz` | 马丁·舒华兹 | 交易/动量 |
| 6 | `larry-williams` | 拉瑞·威廉姆斯 | 技术指标 |
| 7 | `michael-steinhardt` | 迈克尔·斯坦哈特 | 宏观对冲 |
| 8 | `jeff-cooper` | 杰夫·库珀 | 量化/风险管理 |
| 9 | `george-douglas-taylor` | 乔治·道格拉斯·泰勒 | 交易系统 |
| 10 | `junshan-jushi` | 君山居士（康会民） | 中国民间流派 |
| 11 | `qin-guoan` | 秦国安 | 中国民间流派 |
| 12 | `xu-wenming` | 徐文明 | 中国民间流派 |
| 13 | `long-qitian` | 龙祺天 | 中国民间流派 |
| 14 | `yang-jiyuan` | 杨济源 | 中国民间流派 |
| 15 | `yeshan-zhangwenhua` | 野山（张文华） | 中国民间流派 |

> 这 15 人恰好是"技术分析 + 中国民间交易流派"整批，印证了 C-2 的历史成因：README 的两张表停留在 36 人时代，后续批量新增的这批人只进了总览表与 registry，没回填这两张表。

### D. `FAQ.md` 与其它文档

| 编号 | 位置 | 问题描述 | 严重度 | 建议修法 | 需人工决策 |
| --- | --- | --- | --- | --- | --- |
| D-1 | `FAQ.md` 变体表 | FAQ 只列 **2** 种变体（完整版/精简版），README 列 **4** 种 → 口径不一致 | 🟡 建议 | 与 C-3 一并统一 | 否 |
| D-2 | `FAQ.md` | 链接 `[combos/](combos/)` 指向目录。GitHub 上可打开，但非文件级深链，读者需再点一层 | 🟡 建议 | 改为指向 `combos/ROUNDTABLE.md` | 否 |

---

## 五、规范歧义点（`SKILL_SPEC.md` 措辞可有两种解读之处）

| # | 条款 | 原文 | 歧义 | 建议措辞 |
| --- | --- | --- | --- | --- |
| 1 | §1 目录结构 | `SKILL-<专项>.md # [可选]`、`SKILL.en.md # [可选]` | 标了 `[可选]`，但 README/FAQ 又把它当作"每个 skill 都支持的变体"来宣传。到底"可选"是"允许不提供"还是"建议提供"？ | 明确写：「可选。若提供，需在 `examples/INDEX.md` 与 README 变体表中同步登记；未提供时不视为不合规」 |
| 2 | §7 examples 规范 | 「至少 3 个示例」+「每个示例包含：输入 + 框架选择 + 完整输出 + 校准说明」 | 未说明"示例"是**独立文件**还是**可写在 `INDEX.md` 内的段落**。当前 51 个 skill 都理解为"独立文件"却一个都没写。 | 明确写：「至少 3 个**独立 `.md` 文件**（`example-01-*.md` 起），`INDEX.md` 仅作索引，不计入数量」 |
| 3 | §8 治理文件 | `LICENSE # 开源协议（MIT） # 必需（仓库根目录）` | 只规定"MIT"，未规定著作权人署名格式。对"致敬已故人物"的项目，署名写个人、写"contributors"、还是写 Agent 工具，语义差别很大（gaoshanwen-skill 就因此踩坑，见附录） | 明确写：「LICENSE 采用**未经改动的标准 MIT 全文**；致敬/伦理声明放在 `NOTICE` 或 README 末尾，**不要插入 LICENSE 正文**（会破坏 GitHub 协议识别）」 |
| 4 | §9 验收清单 | 「`08-style-anti-patterns.md`：至少 4 个反例」 | 未定义"一个反例"的边界：是必须有 `## 反例 N` 标题，还是 `### 错误输出/为什么不像/正确改写` 三元组齐备才算？当前 36 个达标的都是标准四段式，11 个只有 1 个的也符合四段式结构。 | 明确写：「每个反例须含 `## 反例 N：<主题>` 标题且下辖「错误输出 / 为什么不像 / 正确改写」三个子节，缺一不计」 |
| 5 | §3 SKILL.md 正文结构 | 列了 9 个"必须包含"区块 | 未说明**区块标题的字面要求**。实测 51 个 skill 都用了近似标题（如"核心思维模型（必须掌握）"而非"核心思维模型"），若日后 CI 严格按字面匹配会大面积误报 | 明确写：「区块标题需以指定词开头（允许附加括号说明），CI 用前缀匹配」 |
| 6 | §9 质量检查 | 「如人物已故，含致敬与伦理声明」 | 未定义"已故"如何判定、声明放在哪个文件、需要什么措辞。实测 11 个已故人物都在 `SKILL.md` 或 `PROFILE.md` 里有相关表述，但措辞各异 | 明确写：「已故人物需在 `PROFILE.md` 首次出现处标注生卒年，并在 `SKILL.md` 定位声明中加一句致敬」 |
| 7 | 全文 | 通篇未提及 `registry/` 的维护责任 | `SKILL_SPEC.md` 只管单个 skill 目录，完全没写 `registry/index.json` 与 `roundtable-matrix.json` 必须与 `skills/` 保持一致、版本号如何递增。这正是 A-1/A-2 长期未被发现的制度原因 | 新增一节「registry 维护约定」：字段定义、与 `CODE_MAP`/`STAGE_MAP` 的单一来源关系、版本号递增规则、CI 校验要求 |

---

## 附录 A：基线勘误（你的基线有 5 处与实际不符，以本报告实测为准）

| 基线原文 | 实测 | 证据 |
| --- | --- | --- |
| 圆桌会议表 18 组 | **19 组** | `sed -n '527,554p' README.md \| grep -c '^\|'` → 21（减表头 2 行） |
| 专家角色表 37 行 | **36 行** | `sed -n '555,597p' README.md \| grep -c '^\|'` → 38（减表头 2 行） |
| 快速开始 7 个平台路径 | **6 个**（兼容性表才是 7 行） | 快速开始表 6 行；兼容性表 7 行 |
| gaoshanwen：7 份 references + 10 个 examples | **8 份 references**（与 08 已存在一致）+ **13 个 examples**（+INDEX.md = 14 个文件） | `ls -1 references \| wc -l` → 8；`ls -1 examples \| grep -v INDEX.md \| wc -l` → 13 |
| gaoshanwen：版本 1.1.0 vs v1.3.0 | **四种口径并存**，且 HEAD 提交写 **v1.4.2**（CHANGELOG 无 1.4.x 条目） | 见附录 C |

> 其余基线（字节数、无 LICENSE、无 docs/、22 个 details、36 合计、`skills/skills` 存在）**全部与实测吻合**。

---

## 附录 B：gaoshanwen-skill 复核（`401e4fc`，2026-07-09 16:07:33 +0800）

```
HEAD 提交信息：feat: v1.4.2 - add 2026 H2 A-share outlook + Fed pseudo-easing analysis
根目录：LICENSE ✅ / README.en.md ✅ / SKILL.md / SKILL-condensed.md
       / SKILL-a-share.md / SKILL-real-estate.md / SKILL.en.md
       / references(8) / examples(13) / tests(6) / scripts(3) / .github(5 Issue 模板 + PR 模板 + release-drafter + validate.yml)
```

| 编号 | 问题 | 实测 | 严重度 |
| --- | --- | --- | --- |
| G-1 | **LICENSE 被判 NOASSERTION 的根因已定位** | LICENSE 是标准 MIT 正文，但在 `Copyright (c) 2026 mavis (Mavis Agent)` 与 `Permission is hereby granted` 之间**插入了两行致敬语**（`致敬高善文先生（1971-2026）` / `In memory of Mr. Gao Shanwen (1971-2026)`）。这段非标准插入破坏了 GitHub 的协议模板匹配 → `license = NOASSERTION`。CITATION.cff 却写 `license: MIT` | 🟠 重要 |
| G-2 | **版本号四种口径** | 徽章 `Version-1.1.0`；README:566「项目当前状态 v1.3.0」；CITATION.cff `version: "1.2.0"`；HEAD 提交信息 `v1.4.2`；CHANGELOG 最高只有 `1.3.0`（**无 1.4.x 条目**）；`SKILL-a-share.md` / `SKILL-condensed.md` frontmatter 均为 `version: 1.1.0`；FAQ 引文写 `{1.3.0}` | 🟠 重要 |
| G-3 | README 数字过期 | 宣称 examples「10 个」（README:84、:552），实测 **13 个** | 🟡 建议 |
| G-4 | Roadmap 与实际相反 | Roadmap 把 `references/08-style-anti-patterns.md` 列为待办（README:579、:586），但该文件**已存在** | 🟡 建议 |
| G-5 | Roadmap 编号冲突 | Roadmap 计划 `examples/11-debt-cycle.md`、`examples/12-hog-cycle-inflation.md`；实际 `examples/11-2026-h1-a-share-analysis.md`、`examples/12-2026-h2-a-share-outlook.md` 已占用 11/12 号，主题完全不同 | 🟡 建议 |
| G-6 | "53 项校验"宣称**属实** | 实跑 `python scripts/validate-skill.py .` → `总检查项: 53 / 通过: 53 / 失败: 0` | ✅ 通过 |
| G-7 | 作者署名 | README 结尾「本项目由 mavis (Mavis Agent) 创建」，与 LICENSE 著作权人一致。这是**授权链的关键事实**：若 skill-palace 复用其内容，需确认与 `kevin12369` 的关系 | 🟠 重要（P5 前置） |

---

## 附录 C：复现命令集（每个数字都可自行复算）

```bash
# ── 前提：拿到与远端一致的树
cd <repo> && git fetch origin
git rev-list --left-right --count HEAD...origin/main      # 0	0
git archive HEAD | tar -x -C /tmp/sp-audit && cd /tmp/sp-audit

# ── 一、CI 复现
python _audit_ci.py                                        # 51 OK / 0 WARN / 0 ERROR / exit 0

# ── 二、目录口径
git ls-tree -d --name-only HEAD skills/ | wc -l            # 52
git ls-tree -d --name-only HEAD skills/ | grep -v _template | wc -l   # 51
git ls-tree -d --name-only HEAD skills/skills              # 空（未跟踪残留）

# ── 三、README 数字
grep -c 'img.shields.io' README.md                         # 3
sed -n '23,80p' README.md | grep -c '^|'                   # 53 → 51 行数据
sed -n '23,80p' README.md | grep -o '✅' | wc -l            # 51
grep -c '<details>' README.md                              # 22
grep -o '（[0-9] 个 skill）' README.md | ...                # 合计 36
sed -n '527,554p' README.md | grep -c '^|'                 # 21 → 19 组
sed -n '555,597p' README.md | grep -c '^|'                 # 38 → 36 行
find skills -name 'SKILL.en.md' | wc -l                    # 0
find skills -maxdepth 2 -name 'SKILL-*.md' | wc -l         # 52（全是 condensed）
git ls-tree HEAD docs/                                     # 空 → 死链成立
ls LICENSE*                                                # 不存在

# ── 四、registry
python -c "import json;print(len(json.load(open('registry/index.json',encoding='utf-8'))['skills']))"        # 51
python -c "import json;print(len(json.load(open('registry/roundtable-matrix.json',encoding='utf-8'))['experts']))"  # 51
python -c "import json;print(len(json.load(open('registry/roundtable-matrix.json',encoding='utf-8'))['alias_map']))" # 49 ← 缺 2
grep -c '":' <(sed -n '/^CODE_MAP = {/,/^}/p' tools/skill-gen/build.py)   # CODE_MAP 49 条

# ── 五、规范符合性
ls -1 skills/*/examples/*.md | grep -v INDEX.md | wc -l    # 0 ← 示例文件一个都没有
grep -l '^## 反例' skills/*/references/08-style-anti-patterns.md | wc -l  # 部分未达 4 个

# ── 附录 B：gaoshanwen
git clone https://github.com/kevin12369/gaoshanwen-skill.git /tmp/gsw-audit
cd /tmp/gsw-audit && git log -1 --format='%s'              # feat: v1.4.2 ...
python scripts/validate-skill.py .                         # 53/53 通过
head -8 LICENSE                                            # MIT + 插入的致敬两行
ls -1 references | wc -l                                   # 8
ls -1 examples | grep -v INDEX | wc -l                      # 13
```

---

## 优先修复建议（按投入产出排序，供 P1 起执行参考）

1. **P1 LICENSE**（B-3/C-4）—— 一个文件解决两处阻断，且是法律层面的必需项。**需先定著作权署名**。
2. **P2 docs/ 死链**（C-1）—— 正好用 `docs/audit.md` 已创建的空 `docs/` 目录落地两篇设计文档。**需先定补写还是删链接**。
3. **P3 数字统一**（C-2/C-3/C-6 + A-3）—— 把 51 一路对齐；工作量大头在补齐"按领域浏览"13 个缺口与"专家角色"15 个缺口。
4. **A-1/A-2 registry 缺陷** —— 代码级 bug，改 `CODE_MAP` 两行 + 版本常量，重跑 `build.py` 即可，收益高、风险低。
5. **B-2 反例回填**（15 个）—— 优先 4 个旗舰（高善文/格林斯潘/芒格/巴菲特），其余 11 个可直接参照批量模板。
6. **B-1 examples** —— 建议走"如实声明 + 逐步补旗舰"路线，不要一次性补 153 个文件。**这是最需要你拍板的一项**。
7. **P5 授权链** —— 依赖 G-1/G-7 的结论，建议放到最后，等前面全部落地后再定 MIT + NOASSERTION 的处置方式。
