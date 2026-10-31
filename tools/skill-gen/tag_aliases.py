# -*- coding: utf-8 -*-
"""英文查询 → 中文标签的别名表（圆桌组阁的 i18n 入口）。

背景
----
`roundtable-matrix.json` 的 tag_index 有 345 个去重标签，其中 330 个含中文。
`assemble.py` 的路径 A 是 `if tag.lower() in q_lower` 的纯子串匹配，所以**任何英文问题
都命中不了任何标签**，最后必然落到 FALLBACK 的三个兜底专家——英文用户拿到的「圆桌」
永远是同一桌。

本表解决的是「英文问题 → 中文标签」这一步：键是英文短语（按问题里可能出现的写法），
值是该短语应当点亮的**中文标签**（必须是 tag_index 里真实存在的标签，否则无效果）。

覆盖范围（重要）
----------------
这是**起手式**，不是完整方案。原因是标签覆盖率曲线很平：前 50 个标签只覆盖 31% 的
专家-标签对，要 200 个才能到 67%。全量英文化属于 i18n 的 P1 内容工程（见 docs/i18n-plan.md），
本表只覆盖高频 + 领域定义型的标签，让英文查询能进入组阁而不是直接掉进兜底。

补法：往 EN_TAG_ALIASES 里加条目即可，不需要改 assemble.py。加完跑
`python scripts/check_roundtable_en.py` 看回归是否通过。
"""

# 英文短语（小写，按子串匹配） -> 应点亮的中文标签列表
EN_TAG_ALIASES: dict[str, list[str]] = {
    # ---------- 交易纪律 / 风险 ----------
    "stop loss": ["止损", "止盈止损"],
    "stop-loss": ["止损", "止盈止损"],
    "risk management": ["风险控制"],
    "risk control": ["风险控制"],
    "position sizing": ["资金管理"],
    "money management": ["资金管理"],
    "drawdown": ["止损"],
    "discipline": ["纪律"],
    "systemic risk": ["系统性风险"],
    # ---------- 市场情绪 / 行为金融 ----------
    "market sentiment": ["市场情绪", "市场心理"],
    "sentiment": ["市场情绪"],
    "market psychology": ["市场心理", "投资者行为"],
    "investor behavior": ["投资者行为"],
    "investor behaviour": ["投资者行为"],
    "behavioral finance": ["行为金融"],
    "behavioural finance": ["行为金融"],
    "irrational exuberance": ["非理性繁荣", "泡沫"],
    "bubble": ["泡沫"],
    "prevailing bias": ["主流偏见"],
    "main force": ["主力", "主力行为"],
    # ---------- 价值投资 / 微观决策 ----------
    "value investing": ["价值投资"],
    "intrinsic value": ["估值", "安全边际"],
    "margin of safety": ["安全边际"],
    "moat": ["护城河"],
    "valuation": ["估值"],
    "peg ratio": ["PEG"],
    "garp": ["GARP"],
    "cape ratio": ["CAPE"],
    "tenbagger": ["tenbagger"],
    "concentrated": ["集中投资"],
    "long-term holding": ["长期持有", "长期投资"],
    "buy and hold": ["长期持有"],
    "management quality": ["管理层"],
    "quality of management": ["管理层"],
    "stock picking": ["选股"],
    "stock selection": ["选股"],
    # ---------- 技术分析 ----------
    "technical analysis": ["A股技术分析", "技术面"],
    "support and resistance": ["支撑阻力"],
    "support/resistance": ["支撑阻力"],
    "volume and price": ["量价分析", "量价"],
    "volume-price": ["量价分析", "量价"],
    "volume": ["成交量"],
    "moving average": ["均线"],
    "macd": ["MACD"],
    "rsi": ["RSI"],
    "kdj": ["KDJ"],
    "obv": ["OBV"],
    "candlestick": ["K线"],
    "fibonacci": ["斐波那契"],
    "divergence": ["背离"],
    "momentum": ["动量"],
    "trend following": ["趋势交易"],
    "trend": ["趋势"],
    "reversal": ["反转"],
    "mean reversion": ["均值回归"],
    # ---------- 组合 / 资产配置 ----------
    "asset allocation": ["资产配置", "大类资产"],
    "asset class": ["大类资产"],
    "index investing": ["指数投资"],
    "index fund": ["指数投资"],
    # ---------- 宏观 ----------
    "liquidity": ["流动性"],
    "monetary policy": ["货币政策"],
    "federal reserve": ["美联储"],
    "fed ": ["美联储"],
    "interest rate": ["利率"],
    "exchange rate": ["汇率"],
    "currency": ["汇率"],
    "global macro": ["全球宏观", "中美宏观"],
    "macro hedge": ["宏观对冲", "全球宏观"],
    "debt cycle": ["债务周期"],
    "deleveraging": ["去杠杆"],
    "business cycle": ["周期"],
    "economic cycle": ["周期"],
    "china macro": ["中国宏观"],
    # ---------- A 股 / 短线 ----------
    "a-share": ["A股", "A股实战"],
    "a-shares": ["A股", "A股实战"],
    "china stock market": ["中国股市", "A股"],
    "day trading": ["短线交易", "短线"],
    "short-term trading": ["短线交易", "短线"],
    "short term trading": ["短线交易", "短线"],
    "swing trading": ["短线交易", "短线"],
    "limit-up": ["一字板"],
    "event driven": ["事件驱动"],
    # ---------- 系统化 / 方法论 ----------
    "systematic trading": ["系统化"],
    "quantitative": ["系统化"],
    "hype cycle": ["Hype Cycle"],
    "canslim": ["CANSLIM"],
    "scuttlebutt": ["scuttlebutt"],
    "skin in the game": ["skin in the game"],
    "lollapalooza": ["Lollapalooza"],
    "innovation cluster": ["创新集群"],
    "uncertainty": ["不确定性"],
}
