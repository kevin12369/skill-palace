# 圆桌会议机制（Roundtable）

## 核心理念

不是"预设组合"，而是"按需组阁"。用户提出一个问题，系统根据问题涉及的领域，**动态组装**最合适的专家圆桌。

> 不是"你要用宏观智囊团"，而是"你的问题涉及中美宏观 + 微观估值，所以我帮你组一个圆桌：gao-shanwen（中国宏观）+ greenspan（全球宏观）+ warren-buffett（估值）"

**标识符约定**：每位专家以 **slug**（如 `gao-shanwen` / `junshan-jushi`）为**唯一主键**；圆括号里的 2 字母**短代码**（如 GS / JS）仅为**展示别名**，集中定义在 `tools/skill-gen/build.py` 的 `CODE_MAP`，由构建脚本统一生成并做**冲突检测**——新增人物无需在多处手动同步代码，也绝不会再出现"西蒙斯被迫用 JM 因 JS 已被君山居士占用"这类静默冲突。

**低 token 原则**：组阁时优先读本节"快速组阁速查" + `registry/roundtable-matrix.json`，**不要**逐个读取 51 份完整 SKILL.md。仅在确定席位后，才加载被选中专家的 SKILL.md（其路径见 matrix 的 `path` 字段）。

---

## 快速组阁速查（低 token 模式）★

本表是组阁的唯一必读入口。机器可读版见 `registry/roundtable-matrix.json`（字段更小、可直接程序化检索）。

### 1. 专家标识（slug 主键 + 短代码别名）

| slug（主键） | 代码 | 人物 | slug（主键） | 代码 | 人物 |
|------|------|------|------|------|------|
| **gao-shanwen** | GS | 高善文 | **carlota-perez** | CP | 卡洛塔·佩雷斯 |
| **greenspan** | GP | 格林斯潘 | **kondratiev** | KN | 康德拉季耶夫 |
| **warren-buffett** | WB | 沃伦·巴菲特 | **george-soros** | SZ | 乔治·索罗斯 |
| **charlie-munger** | CM | 查理·芒格 | **irving-fisher** | IF | 欧文·费雪（大） |
| **philip-fisher** | PF | 菲利普·费雪（小） | **hyman-minsky** | HM | 海曼·明斯基 |
| **ray-dalio** | RD | 瑞·达里奥 | **joseph-schumpeter** | SP | 约瑟夫·熊彼特 |
| **gartner-hype-cycle** | GT | 加特纳 Hype Cycle | **theodore-wright** | WR | 西奥多·莱特 |
| **william-jevons** | JV | 威廉·杰文斯 | **howard-marks** | HOM | 霍华德·马克斯 |
| **burton-malkiel** | BM | 伯顿·马尔基尔 | **fred-schwed** | FS | 弗雷德·施韦德 |
| **daniel-kahneman** | DK | 丹尼尔·卡尼曼 | **qiu-guolu** | QG | 邱国鹭 |
| **liu-shunren** | LS | 刘顺仁 | **john-gordon** | JG | 约翰·戈登 |
| **robert-shiller** | RS | 罗伯特·席勒 | **charles-ellis** | CE | 查尔斯·埃利斯 |
| **nassim-taleb** | NT | 纳西姆·塔勒布 | **ben-bernanke** | BB | 本·伯南克 |
| **duan-yongping** | DY | 段永平 | **li-daxiao** | LD | 李大霄 |
| **hong-hao** | HH | 洪灏 | **peter-lynch** | PL | 彼得·林奇 |
| **fu-peng** | FP | 付鹏 | **xu-xiang** | XX | 徐翔 |
| **beijing-chaojia** | BC | 北京炒家 | **jesse-livermore** | JL | 杰西·利弗莫尔 |
| **william-gann** | WG | 威廉·江恩 | **michael-steinhardt** | SH | 迈克尔·斯坦哈特 |
| **martin-schwartz** | MZ | 马丁·舒华兹 | **larry-williams** | LW | 拉瑞·威廉姆斯 |
| **joseph-granville** | GR | 约瑟夫·格伦维尔 | **richard-wyckoff** | RW | 理查德·威科夫 |
| **george-douglas-taylor** | GD | 乔治·道格拉斯·泰勒 | **jeff-cooper** | JC | 杰夫·库珀 |
| **yeshan-zhangwenhua** | YS | 野山（张文华） | **junshan-jushi** | JS | 君山居士（康会民） |
| **xu-wenming** | XW | 徐文明 | **qin-guoan** | QA | 秦国安 |
| **long-qitian** | LQ | 龙祺天 | **yang-jiyuan** | YJ | 杨济源 |
| **james-simons** | JM | 詹姆斯·西蒙斯 | **stanley-druckenmiller** | SD | 斯坦利·德鲁肯米勒 | **william-oneil** | WO | 威廉·欧奈尔 |

### 2. 领域标签 → 专家 slug 映射（代码为展示别名）

| 标签 | 候选 slug（代码） | 标签 | 候选 slug（代码） |
|------|---------|------|---------|
| 中国宏观 / 资产定价 / 地产 / 人口 / 汇率 | **gao-shanwen (GS)** | 反身性 / 繁荣-萧条 / 宏观转折 | **george-soros (SZ)** |
| 全球宏观 / 美联储 / 利率 / 美元 / 跨境资本 | **greenspan (GP)** | 技术周期 / 范式转型 / 导入-展开期 / 转折点 | **carlota-perez (CP)** |
| 泡沫识别 / 非理性繁荣 / 风险识别 | **greenspan (GP), charlie-munger (CM), george-soros (SZ), hyman-minsky (HM), carlota-perez (CP)** | 长波 / 康波 / 创新集群 / 地缘周期 | **kondratiev (KN)** |
| 价值投资 / 护城河 / 估值 / 安全边际 / 管理层 | **warren-buffett (WB), philip-fisher (PF)** | 通缩 / 债务周期 / 资产负债表衰退 | **irving-fisher (IF)** |
| 微观决策 / 逆向思考 / 偏误 / Lollapalooza | **charlie-munger (CM)** | 成长股 / scuttlebutt / 15点 / 研发 | **philip-fisher (PF)** |
| 金融不稳定 / 明斯基时刻 / 庞氏 / 信贷脆弱性 | **hyman-minsky (HM)** | 债务周期 / 去杠杆 / 全天候 / 大国兴衰 | **ray-dalio (RD)** |
| 创造性破坏 / 企业家 / 创新集群 / 产业突变 | **joseph-schumpeter (SP)** | 杰文斯悖论 / 效率悖论 / 资源约束 / 能源 | **william-jevons (JV)** |
| 企业质量 / 商业判断 | **charlie-munger (CM), warren-buffett (WB)** | 莱特定律 / 学习曲线 / 成本预测 / 规模化 | **theodore-wright (WR)** |
| | | Hype Cycle / 技术成熟度 / 幻灭低谷 | **gartner-hype-cycle (GT)** |
| 周期 / 风险控制 / 第二层次思维 / 钟摆 / 防御 | **howard-marks (HOM)** | 有效市场 / 指数投资 / 资产配置 / 长期投资 | **burton-malkiel (BM)** |
| 行为金融 / 认知偏差 / 损失厌恶 / 前景理论 | **daniel-kahneman (DK)** | 市场荒诞 / 人性 / 投资者行为 / 利益错位 | **fred-schwed (FS)** |
| 中国价值投资 / 护城河 / 数月亮 / 便宜是硬道理 | **qiu-guolu (QG)** | 财报质量 / 财务分析 / 战略 / 公司治理 | **liu-shunren (LS)** |
| 金融史 / 市场制度 / 危机记忆 / 长期视角 | **john-gordon (JG)** | 行为泡沫 / 叙事经济学 / CAPE / 非理性繁荣 | **robert-shiller (RS)** |
| 投资政策 / 再平衡 / 输家的游戏 / 长期纪律 | **charles-ellis (CE)** | 黑天鹅 / 尾部风险 / 反脆弱 / 凸性 / 杠铃 | **nassim-taleb (NT)** |
| 货币政策 / 美联储 / 金融危机 / 信用传导 / 流动性 | **ben-bernanke (BB)** | | |
| 商业模式 / 本分 / 不懂不做 / 买股票即买公司 / 企业质量 | **duan-yongping (DY)** | A股 / 政策市 / 牛熊底部 / 蓝筹 / 市场情绪 | **li-daxiao (LD)** |
| A股策略 / 信用周期 / 流动性 / 资金流 / 均值回归 | **hong-hao (HH)** | 成长股 / PEG / 十倍股 / 逛商店选股 | **peter-lynch (PL)** |
| 宏观对冲 / 利率 / 汇率 / 债券 / 大类资产 / 风险定价 | **fu-peng (FP)** | | |
| 短线交易 / 涨停板 / 打板 / 龙头战法 / 题材博弈 | **xu-xiang (XX), beijing-chaojia (BC)** | 趋势交易 / 情绪周期 / 投机 / 坐等 / 关键点 | **jesse-livermore (JL), larry-williams (LW)** |
| 江恩理论 / 时间周期 / 角度线 / 几何 / 共振 | **william-gann (WG)** | 宏观催化剂 / 信息优势 / 事件驱动 / 灵活多空 | **michael-steinhardt (SH)** |
| 动量交易 / 指标共振 / 止损纪律 / 复盘 | **martin-schwartz (MZ), larry-williams (LW)** | 量价分析 / OBV / 格伦维尔法则 / 背离 | **joseph-granville (GR), richard-wyckoff (RW)** |
| 威科夫操盘法 / 吸筹 / 派发 / 弹簧效应 | **richard-wyckoff (RW)** | 泰勒交易法 / 三日子 / 日内周期 | **george-douglas-taylor (GD)** |
| 摆动交易 / Hit and Run / Setup / 扩张序列 | **jeff-cooper (JC)** | 中国技术分析 / 波段 / 均线 / 主力行为 | **yeshan-zhangwenhua (YS), junshan-jushi (JS), xu-wenming (XW), qin-guoan (QA)** |
| 交易心理学 / 风险控制 / 系统化交易 | **yang-jiyuan (YJ), long-qitian (LQ), martin-schwartz (MZ)** | | |
| 量化投资 / 统计套利 / 因子模型 / 高频 / 壁虎式 / 多策略 / 算法 | **james-simons (JM)** | 宏观投资 / 非对称风险收益 / 资本保全 / 增长动量 / 流动性 / 联储政策 / 集中投资 | **stanley-druckenmiller (SD)** | CANSLIM / 杯柄形态 / 带量突破 / 相对强度 / 止损纪律 / 龙头股 / 市场方向 | **william-oneil (WO)** |

> 完整标签索引（345 个）见 `registry/roundtable-matrix.json` 的 `tag_index`，此处仅列高频入口。

### 3. 确定性排序与候选收敛

圆桌遵循固定分析顺序：**宏观定调 → 中观筛选 → 微观决策**。组阁后按确定性规则收敛（v2.1 升级，落地方案见 `tools/skill-gen/assemble.py`）：

1. **四条命中路径**（v2.7.1 起支持英文问题）：
   - **A) 中文标签直接命中**：问题文本包含 `tag_index` 里的中文标签（子串匹配，忽略大小写）。
   - **A') 英文别名命中**：问题里的英文短语经 `tools/skill-gen/tag_aliases.py` 的 `EN_TAG_ALIASES` 映射回中文标签，再走同一套加权。**不加这条，英文问题会命中 0 个标签，恒定落到三个兜底专家**——那不是「效果差」，是组阁失效。
   - **B) 口语兜底词表**："上车/该不该买/抄底/追高"等高频中文问法 → 候选 slug，解决字面匹配弱的问题。
   - **C) domain slug 命中**：`domain` 字段本身就是英文（`value-investing`、`short-term-trading`…），把问题按非字母数字切词后，若某专家的 domain 拆词全部出现，即命中。这是**零翻译成本**的英文入口。
2. **命中强度**：A / A' 命中计 2 分、B / C 命中计 1 分，累加；排序键 =（阶段顺序 → 强度降序 → slug 字母序）。同一标签被 A 与 A' 同时点亮只计一次。
3. **阶段限额**：宏观定调 ≤3、中观筛选 ≤2、微观决策 ≤2。
4. **兜底补位**：某阶段为空时补位——宏观空补 **gao-shanwen（GS）**、中观空补 **charlie-munger（CM）**、微观空补 **warren-buffett（WB）**（保证三阶段齐全）。
5. **情境补位**：问题命中特定模式时按序补入，弥补结构性盲区（A股/中国 → gao-shanwen+hong-hao；美联储/降息 → greenspan+ben-bernanke；科创/科技/AI → robert-shiller+howard-marks+carlota-perez；消费/白酒 → qiu-guolu+duan-yongping；新能源 → peter-lynch+theodore-wright；金融/地产/红利 → li-daxiao+qiu-guolu）。
6. **列席备询**：正式之外的命中者按序取 ≤6 人，不占正式名额。
7. **微观决策至少 1 人**：即使零命中，也补 warren-buffett 作最终裁决者。

### 4. 组阁算法（伪代码）

```
1. 解析用户问题
2. 路径A ：问题匹配 tag_index 中文标签 → 取候选 slug（命中 +2）
3. 路径A'：英文短语经 EN_TAG_ALIASES 映射回中文标签 → 同上（命中 +2，与 A 去重）
4. 路径B ：口语兜底词表命中 → 取候选 slug（命中 +1）
5. 路径C ：domain slug 拆词全部出现在问题中 → 该专家命中（命中 +1）
6. 合并去重，按 阶段 → 强度 → slug字母 排序
7. 阶段限额截取（宏观≤3 / 中观≤2 / 微观≤2）
8. 空阶段兜底补位（gao-shanwen / charlie-munger / warren-buffett）
9. 情境补位（A股/美联储/科创/消费/新能源/金融等模式）
10. 列席 = 剩余命中者，取 ≤6
11. 仅加载所选 slug 的 SKILL.md（其余不读，省 token）
12. 依次发言 → 交叉验证（共振/分歧）→ 合成最终判断
```

> 可执行版本：`python tools/skill-gen/assemble.py "问题"` 一键复现组阁（`--json` 输出结构化结果，键均为 slug）。主持人可在脚本基线之上微调并注明理由。
>
> 回归：`python scripts/check_roundtable_en.py` —— 固定「英文问题能召回、中文问题不退化、零命中兜底仍完整」三条不变式，已接入 CI。

### 5. 高频问法兜底词表（口语 → 候选 slug，节选）

| 口语 / 问法 | 候选 slug（代码） |
|------|---------|
| 上车 / 买入 / 该不该买 / 值不值得买 | duan-yongping (DY), qiu-guolu (QG), warren-buffett (WB), peter-lynch (PL) |
| 抄底 / 追高 / 止损 / 补仓 | charlie-munger (CM), qiu-guolu (QG), howard-marks (HOM) |
| 泡沫 / 崩盘 / 风险 / 追 | robert-shiller (RS), howard-marks (HOM), nassim-taleb (NT), george-soros (SZ) |
| 牛市 / 熊市 / 底部 / 见顶 / 牛熊 | li-daxiao (LD), hong-hao (HH) |
| 降息 / 加息 / 美联储 / 央行 | ben-bernanke (BB), greenspan (GP), fu-peng (FP) |
| 利率 / 汇率 / 流动性 / 北向 / 资金 | fu-peng (FP), greenspan (GP), hong-hao (HH) |
| 成长 / 十倍 / 科技 / AI / 芯片 / 科创 | peter-lynch (PL), gartner-hype-cycle (GT), carlota-perez (CP), robert-shiller (RS) |
| 赛道 / 龙头 / 茅台 / 银行 / 消费 | qiu-guolu (QG), li-daxiao (LD), duan-yongping (DY) |
| 财报 / 财务 / 审计 / 治理 | liu-shunren (LS), qiu-guolu (QG) |
| 估值 / 贵 / 便宜 / 安全边际 | qiu-guolu (QG), warren-buffett (WB), duan-yongping (DY) |
| 商业模式 / 长期持有 / 价值投资 / 本分 | duan-yongping (DY), warren-buffett (WB) |
| 政策 / 地产 / 通缩 / 债务 / 去杠杆 | li-daxiao (LD), gao-shanwen (GS), irving-fisher (IF), ray-dalio (RD) |
| 指数 / 基金 / 定投 / 配置 / 仓位 | burton-malkiel (BM), charles-ellis (CE), howard-marks (HOM) |

> 完整词表 + 情境补位规则见 `tools/skill-gen/assemble.py`，可随实战持续扩充。

---

## 问题 → 领域匹配逻辑

| 问题特征 | 涉及领域 | 推荐专家（slug，代码） |
|---------|---------|---------|
| 中国经济 / 政策 / 地产 / 汇率 | 中国宏观 | gao-shanwen (GS) |
| 美联储 / 全球利率 / 美元 / 跨境资本 | 全球宏观 | greenspan (GP) |
| 估值 / 护城河 / 安全边际 / 持有决策 | 价值投资 | warren-buffett (WB)（philip-fisher (PF) 辅助） |
| 商业判断 / 逆向审视 / 认知偏误 / Lollapalooza | 微观决策 | charlie-munger (CM) |
| 牛市狂热 / 一边倒舆论 / 泡沫信号 | 风险识别 | greenspan (GP) + charlie-munger (CM)（+ george-soros (SZ) / hyman-minsky (HM) 强化） |
| 企业护城河质量 / 管理层诚信 | 企业质量 | warren-buffett (WB) + charlie-munger (CM) |
| 全球宏观传导至中国资产 | 跨境宏观 | gao-shanwen (GS) + greenspan (GP) |
| 技术革命 / AI 主题 / 产业范式切换 | 技术周期 | carlota-perez (CP) + joseph-schumpeter (SP)（+ gartner-hype-cycle (GT) / theodore-wright (WR) 定位） |
| 债务 / 通缩 / 去杠杆 / 系统性风险 | 金融脆弱性 | irving-fisher (IF) + hyman-minsky (HM) + ray-dalio (RD) |
| 投资该不该做（完整决策链） | 全链路 | gao-shanwen/greenspan（宏观）→ charlie-munger/george-soros（筛选）→ warren-buffett（裁决） |

---

## 圆桌工作流

```
1. 解析用户问题 → 识别涉及的领域标签
2. 按领域标签匹配专家 slug（每领域最少1人，跨领域可多人）
3. 确定分析顺序（宏观 → 中观/筛选 → 微观/估值）
4. 依次调用各专家视角分析（仅加载已选 SKILL.md，路径见 matrix.path）
5. 交叉验证：专家的判断是否共振？分歧在哪？
6. 综合输出：呈现各专家视角 + 分歧点 + 综合判断
```

---

## 专家清单（51 人，slug 主键）

| slug（主键） | 代码 | 人物 | 领域标签（roundtable_tags） | 圆桌角色 | 阶段 | 风格 |
|------|------|------|---------|---------|------|------|
| **gao-shanwen** | GS | 高善文 | 中国宏观、资产定价、房地产、人口、货币政策、汇率 | 中国宏观背景提供者 | 宏观定调 | 隐喻化、方法论先行 |
| **greenspan** | GP | 格林斯潘 | 全球宏观、美联储、利率、美元、跨境资本、泡沫识别、非理性繁荣 | 全球宏观背景提供者 | 宏观定调 | Fedspeak、数据驱动、谨慎 |
| **kondratiev** | KN | 康德拉季耶夫 | 长波、康波、创新集群、周期、价格长波、萧条、创造性毁灭、地缘政治周期 | 长周期分析师 | 宏观定调 | 结构周期、历史纵深 |
| **irving-fisher** | IF | 欧文·费雪（大） | 通缩、债务周期、货币数量论、费雪方程、实际利率、名义利率、货币政策、资产负债表衰退 | 货币与债务周期理论家 | 宏观定调 | 数量化、债务-通缩框架 |
| **ray-dalio** | RD | 瑞·达里奥 | 债务周期、去杠杆、经济机器、全天候、生产率、大国兴衰、资产配置、原则决策 | 债务周期分析师与宏观配置师 | 宏观定调 | 模板化、原则决策 |
| **george-soros** | SZ | 乔治·索罗斯 | 反身性、繁荣-萧条、泡沫、可错性、主流偏见、宏观转折、系统性风险、金融炼金术 | 反身性理论家与泡沫剖析者 | 宏观定调 | 反身性、拐点敏感 |
| **charlie-munger** | CM | 查理·芒格 | 微观决策、逆向思考、偏误扫描、Lollapalooza、商业判断、企业质量、风险识别 | 首席逆向质疑者 | 中观筛选 | 犀利直白、警句式、冷幽默 |
| **hyman-minsky** | HM | 海曼·明斯基 | 金融不稳定、明斯基时刻、庞氏融资、系统性风险、信贷周期、脆弱性、去杠杆、最后贷款人 | 金融不稳定分析师 | 中观筛选 | 脆弱性、信贷周期 |
| **carlota-perez** | CP | 卡洛塔·佩雷斯 | 技术革命、范式转型、导入期、展开期、金融资本、生产资本、泡沫、转折点 | 技术周期分析师 | 中观筛选 | 结构性叙事、周期直觉 |
| **joseph-schumpeter** | SP | 约瑟夫·熊彼特 | 创造性破坏、企业家精神、创新集群、演化经济学、产业突变、新组合、技术颠覆、资本主义演化 | 创新与产业演化理论家 | 中观筛选 | 演化、创新驱动 |
| **gartner-hype-cycle** | GT | 加特纳 Hype Cycle | Hype Cycle、技术成熟度、期望膨胀、幻灭低谷、炒作周期、跨越鸿沟、技术采纳、创新扩散 | 技术成熟度定位分析师 | 中观筛选 | 成熟度曲线、阶段定位 |
| **theodore-wright** | WR | 西奥多·莱特 | 莱特定律、学习曲线、经验曲线、成本预测、制造业、规模化、光伏、电池、干中学 | 技术成本曲线分析师 | 中观筛选 | 成本曲线、规模化 |
| **william-jevons** | JV | 威廉·杰文斯 | 杰文斯悖论、效率悖论、边际效用、资源约束、反弹效应、能源转型、技术进步、数学经济 | 资源效率悖论分析师 | 中观筛选 | 悖论、资源约束 |
| **warren-buffett** | WB | 沃伦·巴菲特 | 价值投资、护城河、估值、安全边际、管理层、资本配置、长期持有 | 估值与最终决策者 | 微观决策 | 朴实平易、故事化、长期 |
| **philip-fisher** | PF | 菲利普·费雪（小） | 成长股、scuttlebutt、15点清单、管理层、研发、长期持有、集中投资、定性分析 | 成长股识别与管理层评估师 | 微观决策 | 定性深挖、scuttlebutt |
| **howard-marks** | HOM | 霍华德·马克斯 | 周期、风险控制、逆向、市场情绪、信用、资产配置、第二层次思维、价格与价值、防御性投资 | 周期定位与风险感知者 | 中观筛选 | 审慎克制、备忘录体、格言化 |
| **burton-malkiel** | BM | 伯顿·马尔基尔 | 有效市场假说、指数投资、资产配置、行为偏差、长期投资、随机漫步、投资组合 | 有效市场与被动投资倡导者 | 中观筛选 | 学术严谨、通俗比喻、证据导向 |
| **fred-schwed** | FS | 弗雷德·施韦德 | 人性、市场结构、投资者行为、幽默批判、金融荒诞、佣金激励、客户利益 | 市场荒诞与人性审视者 | 中观筛选 | 辛辣幽默、寓言笔法、自嘲 |
| **daniel-kahneman** | DK | 丹尼尔·卡尼曼 | 行为金融、认知偏差、前景理论、决策心理、损失厌恶、过度自信、启发式 | 行为偏差与决策心理剖析者 | 中观筛选 | 实验严谨、自我怀疑、反直觉 |
| **qiu-guolu** | QG | 邱国鹭 | 价值投资、中国股市、护城河、逆向、行业格局、长期持有、便宜是硬道理、品质-估值-时机 | 中国价值投资实务派 | 微观决策 | 务实朴素、中国式表达、逆向 |
| **liu-shunren** | LS | 刘顺仁 | 财务分析、财报质量、会计、战略、公司治理、现金流、竞争力、数字故事 | 财报质量与战略剖析者 | 微观决策 | 通俗生动、故事化、批判审慎 |
| **john-gordon** | JG | 约翰·戈登 | 金融史、市场制度、长期视角、危机史、资本市场演进、华尔街史、周期记忆 | 金融史与制度演进观察者 | 宏观定调 | 叙事宏大、史料扎实、冷峻幽默 |
| **robert-shiller** | RS | 罗伯特·席勒 | 行为金融、泡沫、估值、叙事经济学、CAPE、非理性繁荣、市场心理、住房 | 行为泡沫与叙事经济学剖析者 | 宏观定调 | 学术严谨、数据驱动、跨学科 |
| **charles-ellis** | CE | 查尔斯·埃利斯 | 指数投资、资产配置、长期投资、投资者行为、投资政策、再平衡、机构视角 | 投资政策与长期纪律设计者 | 中观筛选 | 理性平和、制度视角、长期主义 |
| **nassim-taleb** | NT | 纳西姆·塔勒布 | 黑天鹅、尾部风险、反脆弱、期权、不确定性、凸性、杠铃策略、skin in the game | 尾部风险与反脆弱剖析者 | 中观筛选 | 犀利毒舌、反脆弱思维、经验主义 |
| **ben-bernanke** | BB | 本·伯南克 | 货币政策、美联储、金融危机、信用传导、流动性、宏观审慎、大萧条、债务通缩 | 货币政策与危机传导分析师 | 宏观定调 | 学术严谨、历史纵深、机制清晰 |
| **duan-yongping** | DY | 段永平 | 价值投资、商业模式、企业文化、能力圈、长期持有、集中投资、中国股市、本分、安全边际、买股票即买公司 | 中国价值投资与企业质量评估师 | 微观决策 | 朴素直白、禅意短句、问答式 |
| **li-daxiao** | LD | 李大霄 | A股、政策市、牛熊判断、市场底部、估值、蓝筹、市场情绪、价值投资、风险警示 | A股市场整体判断者 | 宏观定调 | 直白坚定、口语化、术语创造 |
| **hong-hao** | HH | 洪灏 | A股策略、港股、信用周期、流动性、估值、资金流、大类资产、中美宏观、均值回归、周期定位 | 宏观策略与周期定位分析师 | 宏观定调 | 数据驱动、框架清晰、双语 |
| **peter-lynch** | PL | 彼得·林奇 | GARP、PEG、十倍股、六类股票、选股、成长股、分散投资、生活经验选股、长期持有、tenbagger | 成长股识别与选股实操派 | 微观决策 | 幽默、生活化、故事化、通俗 |
| **fu-peng** | FP | 付鹏 | 宏观对冲、利率、汇率、债券、流动性、大类资产、风险定价、全球宏观、交易视角、数据拆解 | 宏观对冲与利率汇率分析师 | 宏观定调 | 直给、交易员思维、数据拆解 |
| **xu-xiang** | XX | 徐翔 | 短线交易、题材龙头、涨停板、资金面、技术面、市场情绪、消息面、止损、A股、筹码分析 | 短线交易策略与情绪分析师 | 中观筛选 | 寡言冷静、量价语言、实战派 |
| **beijing-chaojia** | BC | 北京炒家 | 打板、龙头战法、题材周期、短线、资金流、止损、A股、市场情绪、高换手、妖股 | 题材博弈与龙头战法分析师 | 中观筛选 | 直白实战、语录体、果断 |
| **jesse-livermore** | JL | 杰西·利弗莫尔 | 趋势交易、关键点、市场心理、做空、止损、最小阻力、投机、金字塔、情绪周期、坐等 | 趋势交易与市场心理大师 | 中观筛选 | 老派叙事、格言化、冷峻克制 |
| **william-gann** | WG | 威廉·江恩 | 江恩理论、时间周期、角度线、几何分析、方形图、循环、斐波那契、止损 | 时间周期与几何分析大师 | 中观筛选 | 数学几何化、神秘主义色彩、纪律至上 |
| **michael-steinhardt** | SH | 迈克尔·斯坦哈特 | 宏观对冲、信息优势、催化剂、短线灵活、做多与做空、流动性、风险套利、事件驱动、情绪博弈 | 宏观催化剂与灵活交易大师 | 宏观定调 | 嗅觉敏锐、信息驱动、灵活果断 |
| **martin-schwartz** | MZ | 马丁·舒华兹 | 动量交易、超短线、技术指标、自律、止损、资金管理、MACD、RSI、斐波那契 | 动量交易与交易纪律大师 | 中观筛选 | 军人式纪律、直白实战、指标语言 |
| **larry-williams** | LW | 拉瑞·威廉姆斯 | 短线交易、威廉指标、资金管理、季节性、市场广度、持仓量、选股、波动率 | 短线择时与资金管理大师 | 中观筛选 | 精密系统化、资金管理优先、数据驱动 |
| **joseph-granville** | GR | 约瑟夫·格伦维尔 | 量价分析、OBV、格伦维尔法则、移动平均线、择时、成交量、背离、反转、趋势 | 量价分析与择时大师 | 中观筛选 | 量价派、系统化、先验数据、反直觉 |
| **richard-wyckoff** | RW | 理查德·威科夫 | 威科夫操盘法、吸筹、派发、供求关系、量价分析、买卖测试、主力意图、弹簧效应、综合人 | 量价结构与主力意图解读者 | 中观筛选 | 量价解剖学、主力博弈、结构推演 |
| **george-douglas-taylor** | GD | 乔治·道格拉斯·泰勒 | 泰勒交易法、三日子、买入日、卖出日、短线周期、日内、支撑阻力、高低点 | 日内周期与泰勒交易法大师 | 中观筛选 | 机械节奏、简单重复、反趋势思维 |
| **jeff-cooper** | JC | 杰夫·库珀 | 摆动交易、Hit and Run、TBF、序列、反转、动量、一字板、扩张、缺口、五分钟 | 摆动交易与短线模式大师 | 中观筛选 | 机械化、Setup导向、精准果断 |
| **yeshan-zhangwenhua** | YS | 野山（张文华） | 波段操作、A股技术分析、量价、均线、形态、主力、市场情绪、短期节奏、选股、低吸高抛 | A股技术派波段分析师 | 中观筛选 | 接地气、通俗比喻、A股实战 |
| **junshan-jushi** | JS | 君山居士（康会民） | 均线系统、趋势交易、A股技术分析、多周期、背离、MACD、支撑阻力、筹码、成交量 | A股趋势与均线系统分析师 | 中观筛选 | 系统教学、均线派、逻辑清晰 |
| **xu-wenming** | XW | 徐文明 | 短线、A股技术分析、KDJ、MACD、均线、止损、纪律、散户策略、量价、波段 | A股散户短线技术分析师 | 中观筛选 | 散户视角、通俗易懂、纪律导向 |
| **qin-guoan** | QA | 秦国安 | 量价分析、主力行为、A股技术分析、资金、突破、回调、止盈止损、K线、趋势 | A股量价与主力行为分析师 | 中观筛选 | 量价派、主力博弈、实战系统 |
| **long-qitian** | LQ | 龙祺天 | 系统化交易、A股技术分析、形态识别、资金管理、趋势、支撑阻力、止盈止损、操作纪律 | A股系统化技术分析师 | 中观筛选 | 系统化、实战导向、纪律语言 |
| **yang-jiyuan** | YJ | 杨济源 | 交易心理学、风险控制、量价分析、A股实战、止损、资金管理、情绪、自控、纪律、系统化 | A股交易心理与风险分析师 | 中观筛选 | 心理层面、实战派、风控至上、自省 |
| **james-simons** | JM | 詹姆斯·西蒙斯 | 量化投资、统计套利、均值回归、高频交易、多策略、壁虎式、数学模型、因子、风险管理、大奖章、分散化、技术面、系统化、算法、数据挖掘 | 量化投资与统计套利大师 | 中观筛选 | 数学化、系统化、数据驱动、低调神秘 |
| **stanley-druckenmiller** | SD | 斯坦利·德鲁肯米勒 | 宏观投资、非对称风险收益、资本保全、增长动量、市场情绪、流动性、集中投资、联储政策 | 宏观投资与资本保全大师 | 宏观定调 | 果断出击、纪律严明、宏观敏感、保本至上 |
| **william-oneil** | WO | 威廉·欧奈尔 | CANSLIM、杯柄形态、带量突破、相对强度、止损纪律、龙头股、市场方向、选股系统 | CAN SLIM选股与突破交易系统分析师 | 中观筛选 | 系统化选股、图表与技术结合、规则至上、纪律严格 |

> 阶段为默认归位，非硬约束：george-soros 可作中观筛选（繁荣-萧条定位），charlie-munger 可作微观决策（Too Hard 筐判定）。组阁时以问题语义为准微调。

---

## 分析顺序约定

圆桌遵循"宏观定调 → 中观筛选 → 微观决策"的固定分析顺序：

1. **宏观定调**（gao-shanwen / greenspan / kondratiev / irving-fisher / ray-dalio / george-soros / stanley-druckenmiller / john-gordon / robert-shiller / ben-bernanke / li-daxiao / hong-hao / fu-peng / michael-steinhardt）：当前宏观环境对问题的影响，结构性变量判断。
2. **中观筛选**（charlie-munger / george-soros / hyman-minsky / carlota-perez / joseph-schumpeter / gartner-hype-cycle / theodore-wright / william-jevons / howard-marks / burton-malkiel / fred-schwed / daniel-kahneman / charles-ellis / nassim-taleb / xu-xiang / beijing-chaojia / jesse-livermore / william-gann / martin-schwartz / larry-williams / joseph-granville / richard-wyckoff / george-douglas-taylor / jeff-cooper / yeshan-zhangwenhua / junshan-jushi / xu-wenming / qin-guoan / long-qitian / yang-jiyuan / james-simons / william-oneil）：逆向审视 + 偏误扫描 + Lollapalooza 风险识别 + 周期/泡沫/脆弱性/行为定位 + 量价/趋势/形态/交易心理/量化统计套利/CAN SLIM选股分析。在此阶段判定是否进入 Too Hard 筐。
3. **微观决策**（warren-buffett / philip-fisher / charlie-munger / qiu-guolu / liu-shunren / duan-yongping / peter-lynch）：估值、护城河、安全边际、管理层、财报质量、商业模式。给出 Yes / No / Too Hard 的最终判断。

---

## 典型圆桌示例

### 示例1："现在的 AI 板块是不是泡沫？应该怎么办？"
- 涉及领域：泡沫识别、逆向审视、估值
- 圆桌成员：greenspan（GS，非理性繁荣）+ charlie-munger（CM，Lollapalooza 扫描 + 逆向）
- 分析顺序：先 greenspan 判断是否构成 irrational exuberance → 再 charlie-munger 做 Lollapalooza 四步扫描 → 综合判断

### 示例2："买入茅台长期持有，这个决策对吗？"
- 涉及领域：中国宏观、护城河、估值、逆向审视
- 圆桌成员：gao-shanwen（GS，中国消费与地产背景）+ warren-buffett（WB，护城河+估值）+ charlie-munger（CM，逆向质疑）
- 分析顺序：gao-shanwen 定调消费宏观环境 → warren-buffett 分析护城河与内在价值 → charlie-munger 做逆向质疑（"茅台会怎样跌 80%"）

### 示例3："美联储降息周期，对 A 股意味着什么？"
- 涉及领域：全球宏观、中国宏观、跨境传导
- 圆桌成员：greenspan（GP，美联储）+ gao-shanwen（GS，A 股传导）
- 分析顺序：greenspan 分析降息路径与全球流动性 → gao-shanwen 分析对中国资产重估的传导

### 示例4："当下美股市场和中国市场是否还能入场投资？"（跨域测试，见 `examples/中美市场入场圆桌实录.md`）
- 涉及领域标签：全球宏观、中国宏观、泡沫识别、估值决策、反身性
- 命中 slug：**greenspan (GS)**（全球宏观 / 泡沫）、**gao-shanwen (GS)**（中国宏观）、**george-soros (SZ)**（反身性 / 繁荣-萧条）、**charlie-munger (CM)**（逆向 / Lollapalooza）、**warren-buffett (WB)**（估值裁决）
- 排序：宏观定调 greenspan + gao-shanwen → 中观筛选 george-soros + charlie-munger → 微观决策 warren-buffett
- 列席备询：gartner-hype-cycle (GT，AI 成熟度)、hyman-minsky (HM，脆弱性)、ray-dalio (RD，去杠杆路径)
- 数据锚点：2026-07-31 收盘
- 结论摘要：
  - 美股"挑着买"——宽基指数安全边际薄、龙头剧烈分化（苹果 -7.35%、特斯拉 YTD -30.8%），避开 PE≈196 的拥挤赛道（科创50），控仓位、设止损。
  - 中国"蓝筹躺着投"——沪深300 PE 14.38 处历史偏低区（价值区间），但负向反身性未破、缺催化，动能交易须等信用扩张与信心逆转信号。
  - **五人共识**：① 美股整体不便宜、安全边际薄；② 科创50 PE≈196 是清晰投机；③ 中美分化是核心矛盾；④ 现金 / 安全边际为共同纪律。
  - **主要分歧**：george-soros 看美股繁荣未尽 vs greenspan 忧非理性繁荣；gao-shanwen 看中国"等催化" vs charlie-munger 忧负面 Lollapalooza 未解；warren-buffett 愿配中国价值 vs george-soros 等叙事转折确认。

### 示例5："当前 A 股能不能上车？"（组阁脚本实测，见 `examples/A股上车圆桌实录.md`）
- 涉及领域标签：A股、中国宏观、牛熊判断、估值、逆向、商业模式
- 脚本命中（`assemble.py`）：标签 A股 + 口语词"上车" → 候选 li-daxiao/duan-yongping/qiu-guolu/warren-buffett/peter-lynch；情境补位 gao-shanwen+hong-hao
- 正式席位：宏观定调 **li-daxiao + gao-shanwen + hong-hao** → 中观筛选 **charlie-munger** → 微观决策 **duan-yongping + peter-lynch**；列席备询 qiu-guolu + warren-buffett
- 数据锚点：2026-08-05（沪深300 PE 14.19、上证 17.68、科创50 PE 200.58）
- 结论摘要：**能上车但上"价值车"不上"行情车"**——沪深300 类低估值蓝筹分 3-4 笔逢低布局；科创50 结构性泡沫（PE 200）坚决回避；留现金、不加杠杆、以"买公司"心态分批。
- 机制改进（本示例驱动的 v2.1 升级）：暴露"候选收敛靠人工、CM 漏选、口语词缺失"三问题 → 落地 `assemble.py`（两级命中 + 阶段限额 + 兜底 + 情境补位），并新增本节口语兜底词表。

---

## 规则

1. **不预设组合**：每次根据问题的具体领域动态组装。
2. **最少 1 人，通常 2-3 人**：单领域问题 1 人即可；跨领域问题 2-3 人（最多 5 正式席位 + 列席备询）。
3. **先宏观后微观**：严格遵守分析顺序。
4. **分歧必须呈现**：不强制统一，标注分歧并做前提审计。
5. **圆桌不替代单一 skill**：简单问题直接调用单一 skill，复杂 / 跨领域问题启动圆桌。
6. **低 token 组阁**：组阁只读本节速查表 + `registry/roundtable-matrix.json`；确定席位后才加载对应 SKILL.md（路径见 matrix.path），不预读全部 profile。
7. **收敛确定性**：组阁可用 `tools/skill-gen/assemble.py` 一键复现（两级命中 → 限额 → 兜底 → 情境补位 → 列席）；主持人在脚本基线之上微调时须注明理由。

---

## 机器索引

`registry/roundtable-matrix.json` 为机器可读的紧凑索引，字段：
- `alias_map`：slug → 短代码（展示别名；专家以 slug 为主键）
- `stages`：三阶段 → slug 列表（宏观定调 / 中观筛选 / 微观决策）
- `experts`：slug → {code, person, role, tags, stage, path}
- `tag_index`：标签 → 候选 slug 列表（332 个标签，供程序化命中）

agent 可据此在单次读取内完成"解析 → 组阁 → 排序"，无需遍历 51 份 SKILL.md。
