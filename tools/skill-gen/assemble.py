# -*- coding: utf-8 -*-
"""圆桌组阁执行脚本：输入问题文本 -> 正式席位 + 列席备询 + 建议数据清单。

用法：
    python assemble.py "当前A股能不能上车"
    python assemble.py "美联储降息对A股意味着什么" --json

设计要点（对应 ROUNDTABLE.md「组阁算法」）：
1. 四条命中路径：A) 问题文本直接匹配中文 tag_index；A') 英文短语经 tag_aliases.EN_TAG_ALIASES
   映射回中文标签（不加这条，英文问题命中 0 标签、恒定落到三个兜底专家）；
   B) 口语兜底词表（解决"能不能上车"类字面匹配弱）；C) domain slug 拆词全中（英文零成本入口）。
2. 确定性收敛：按 阶段顺序 -> 命中强度降序 -> slug 字母序 排序；阶段限额 宏观≤3/中观≤2/微观≤2。
3. 兜底规则：宏观空补 gao-shanwen、中观空补 charlie-munger、微观空补 warren-buffett（保证三阶段齐全）。
4. 列席 = 正式之外的命中者，按序取 ≤6。
5. 建议数据清单：按正式席位阶段聚合。

标识符约定：所有专家以 **slug**（如 gao-shanwen / junshan-jushi）为唯一主键；
圆括号里的 2 字母代码（如 GS / JS）仅为展示别名，定义在 build.py 的 CODE_MAP。
"""

import json
import os
import re
import sys

from tag_aliases import EN_TAG_ALIASES

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAT = os.path.join(ROOT, "registry", "roundtable-matrix.json")

STAGE_ORDER = {"宏观定调": 0, "中观筛选": 1, "微观决策": 2}
LIMITS = {"宏观定调": 3, "中观筛选": 2, "微观决策": 2}
# 兜底专家（slug 主键）
FALLBACK = {"宏观定调": "gao-shanwen", "中观筛选": "charlie-munger", "微观决策": "warren-buffett"}
COLUMN_MAX = 6

# 口语兜底词表：高频问法/口语 -> 候选 slug。值必须存在于 experts，脚本会防御性过滤。
ORAL_MAP = {
    "上车": ["duan-yongping", "qiu-guolu", "warren-buffett", "peter-lynch"], "买入": ["duan-yongping", "qiu-guolu", "warren-buffett", "peter-lynch"],
    "买不买": ["duan-yongping", "qiu-guolu", "warren-buffett", "peter-lynch"], "该不该买": ["duan-yongping", "qiu-guolu", "warren-buffett", "peter-lynch"],
    "值不值得买": ["duan-yongping", "qiu-guolu", "warren-buffett", "peter-lynch"], "抄底": ["charlie-munger", "qiu-guolu", "howard-marks"],
    "追高": ["charlie-munger", "howard-marks", "robert-shiller"], "泡沫": ["robert-shiller", "howard-marks", "greenspan", "george-soros"], "崩盘": ["nassim-taleb", "hyman-minsky"],
    "风险": ["nassim-taleb", "howard-marks", "charlie-munger"], "牛市": ["li-daxiao"], "熊市": ["li-daxiao"], "底部": ["li-daxiao", "hong-hao"],
    "见顶": ["li-daxiao", "robert-shiller"], "牛熊": ["li-daxiao", "hong-hao"], "降息": ["ben-bernanke", "greenspan", "fu-peng"],
    "加息": ["greenspan", "ben-bernanke"], "美联储": ["greenspan", "ben-bernanke"], "央行": ["ben-bernanke", "fu-peng"],
    "利率": ["fu-peng", "greenspan", "ben-bernanke"], "汇率": ["fu-peng", "greenspan", "gao-shanwen"], "流动性": ["hong-hao", "ben-bernanke", "fu-peng"],
    "北向": ["hong-hao"], "资金": ["hong-hao"], "成长": ["peter-lynch", "philip-fisher"], "十倍": ["peter-lynch"],
    "科技": ["gartner-hype-cycle", "carlota-perez", "joseph-schumpeter"], "ai": ["gartner-hype-cycle", "carlota-perez"], "芯片": ["gartner-hype-cycle"],
    "赛道": ["qiu-guolu", "philip-fisher"], "龙头": ["qiu-guolu", "warren-buffett"], "茅台": ["qiu-guolu", "duan-yongping", "warren-buffett"],
    "银行": ["qiu-guolu", "li-daxiao"], "消费": ["qiu-guolu", "warren-buffett"], "财报": ["liu-shunren", "qiu-guolu"], "财务": ["liu-shunren"],
    "审计": ["liu-shunren"], "治理": ["liu-shunren"], "估值": ["qiu-guolu", "warren-buffett", "hong-hao"], "贵": ["qiu-guolu", "robert-shiller"],
    "便宜": ["qiu-guolu", "duan-yongping", "warren-buffett"], "安全边际": ["warren-buffett", "duan-yongping", "charlie-munger"], "商业模式": ["duan-yongping", "warren-buffett"],
    "长期持有": ["duan-yongping", "warren-buffett", "peter-lynch"], "价值投资": ["warren-buffett", "duan-yongping", "qiu-guolu"], "政策": ["li-daxiao", "gao-shanwen", "ben-bernanke"],
    "地产": ["gao-shanwen", "li-daxiao"], "人口": ["gao-shanwen"], "房地产": ["gao-shanwen"], "通缩": ["irving-fisher", "ben-bernanke"],
    "债务": ["irving-fisher", "ray-dalio", "hyman-minsky"], "去杠杆": ["ray-dalio", "hyman-minsky", "irving-fisher"], "信用": ["hong-hao", "ben-bernanke", "hyman-minsky"],
    "衰退": ["ray-dalio", "irving-fisher"], "周期": ["hong-hao", "kondratiev", "howard-marks", "william-gann"], "康波": ["kondratiev"], "长波": ["kondratiev"],
    "不确定性": ["nassim-taleb", "howard-marks"], "尾部": ["nassim-taleb"], "反脆弱": ["nassim-taleb"], "通胀": ["greenspan", "irving-fisher"],
    "非农": ["greenspan"], "补仓": ["qiu-guolu", "warren-buffett", "duan-yongping"], "止损": ["charlie-munger", "nassim-taleb"], "仓位": ["charles-ellis", "howard-marks", "charlie-munger"],
    "配置": ["charles-ellis", "ray-dalio", "burton-malkiel"], "指数": ["burton-malkiel", "charles-ellis"], "基金": ["burton-malkiel", "charles-ellis"], "定投": ["burton-malkiel", "charles-ellis"],
    "股市": ["li-daxiao", "hong-hao", "gao-shanwen"], "大盘": ["li-daxiao", "hong-hao", "gao-shanwen"], "行情": ["hong-hao", "li-daxiao", "gao-shanwen"],
    "走势": ["hong-hao", "li-daxiao"], "经济": ["gao-shanwen", "hong-hao"], "追": ["robert-shiller", "howard-marks", "charlie-munger", "george-soros"],
    "科创": ["robert-shiller", "howard-marks", "gartner-hype-cycle", "carlota-perez"], "还能涨吗": ["robert-shiller", "howard-marks"], "炒": ["robert-shiller", "howard-marks", "fred-schwed"],
    "短线": ["xu-xiang", "beijing-chaojia", "charlie-munger", "martin-schwartz", "jesse-livermore"], "打板": ["beijing-chaojia", "xu-xiang"], "涨停": ["xu-xiang", "beijing-chaojia"],
    "错过": ["charlie-munger", "duan-yongping", "howard-marks"], "观望": ["charlie-munger", "howard-marks", "charles-ellis"], "题材": ["xu-xiang", "beijing-chaojia", "george-soros"],
    "趋势": ["jesse-livermore", "larry-williams", "junshan-jushi"], "关键点": ["jesse-livermore"], "投机": ["jesse-livermore", "george-soros"],
    "技术分析": ["william-gann", "joseph-granville", "yeshan-zhangwenhua", "junshan-jushi", "qin-guoan"], "量价": ["joseph-granville", "richard-wyckoff", "qin-guoan", "yeshan-zhangwenhua"],
    "江恩": ["william-gann"], "波段": ["yeshan-zhangwenhua", "xu-wenming", "jesse-livermore"],
    "日内": ["george-douglas-taylor", "jeff-cooper", "martin-schwartz"], "缺口": ["jeff-cooper", "george-douglas-taylor"], "摆动": ["jeff-cooper"],
    "主力": ["qin-guoan", "richard-wyckoff", "yeshan-zhangwenhua"], "假突破": ["richard-wyckoff"], "吸筹": ["richard-wyckoff"], "派发": ["richard-wyckoff"],
    "复盘": ["martin-schwartz", "yang-jiyuan"], "心态": ["yang-jiyuan", "martin-schwartz"], "风控": ["yang-jiyuan", "larry-williams", "martin-schwartz"],
    "系统": ["larry-williams", "long-qitian", "yang-jiyuan"], "形态": ["long-qitian", "yeshan-zhangwenhua"], "均线": ["junshan-jushi", "yeshan-zhangwenhua", "xu-wenming"],
    "MACD": ["martin-schwartz", "junshan-jushi", "xu-wenming"], "KDJ": ["xu-wenming"], "布林": ["martin-schwartz", "joseph-granville"],
    "威廉": ["larry-williams"], "OBV": ["joseph-granville"], "资金管理": ["larry-williams", "martin-schwartz", "yang-jiyuan"],
    "量化": ["james-simons", "larry-williams", "martin-schwartz"], "统计套利": ["james-simons"], "因子": ["james-simons"], "高频": ["james-simons", "jeff-cooper"],
    "西蒙斯": ["james-simons"], "算法": ["james-simons"], "数据挖掘": ["james-simons"],
}

# 情境补位规则：问题命中模式 -> 按序补位（限额未满才补；已满则进列席）。
# 解决"中国/A股问题缺宏观三人""科技泡沫问题缺泡沫专家"等字面命中的结构性盲区。
CONTEXT_RULES = [
    (r"A股|股市|大盘|中国", ["gao-shanwen", "hong-hao", "li-daxiao"]),
    (r"美联储|降息|加息|美元|全球|美元指数", ["greenspan", "ben-bernanke", "fu-peng"]),
    (r"科创|芯片|AI|科技|半导体", ["robert-shiller", "howard-marks", "gartner-hype-cycle", "george-soros"]),
    (r"消费|白酒|食品|医药|家电", ["qiu-guolu", "duan-yongping", "warren-buffett"]),
    (r"新能源|电池|光伏|储能|电动车", ["peter-lynch", "theodore-wright", "gartner-hype-cycle"]),
    (r"银行|保险|地产|红利|高股息", ["li-daxiao", "qiu-guolu", "irving-fisher"]),
    (r"短线|打板|涨停|题材", ["xu-xiang", "beijing-chaojia", "charlie-munger", "jesse-livermore"]),
    (r"技术分析|量价|趋势|波段|均线|MACD|K线", ["joseph-granville", "richard-wyckoff", "yeshan-zhangwenhua", "junshan-jushi", "qin-guoan"]),
    (r"江恩|时间周期|角度线", ["william-gann"]),
    (r"主力|吸筹|派发|操盘", ["richard-wyckoff", "qin-guoan", "yeshan-zhangwenhua"]),
    (r"复盘|心态|纪律|资金管理", ["martin-schwartz", "yang-jiyuan", "larry-williams"]),
    (r"量化|统计套利|因子模型|高频交易|算法|西蒙斯", ["james-simons"]),
]

# 建议数据清单：按阶段 -> 建议拉取的数据类别
DATA_PLAN = {
    "宏观定调": ["宽基指数行情与估值（沪深300/上证/创业板/科创50 PE）", "宏观与政策（LPR/社融/利率/汇率）"],
    "中观筛选": ["指数估值分位（PE/PB 历史分位）", "市场情绪/资金流（北向、量能）"],
    "微观决策": ["候选个股行情与估值（PE/PB/股息）", "个股财务与财报质量"],
}


def load_matrix():
    with open(MAT, encoding="utf-8") as f:
        return json.load(f)


def assemble(question, column=COLUMN_MAX):
    m = load_matrix()
    experts, tag_index = m["experts"], m["tag_index"]
    q_lower = question.lower()
    strength = {}  # slug -> (A命中数, B命中数)

    def add(slug, kind):
        d = strength.setdefault(slug, [0, 0])
        d[0 if kind == "A" else 1] += 1

    hit_tags = []
    # 路径 A：标签在问题中出现（忽略大小写子串）
    for tag in tag_index:
        if tag.lower() in q_lower:
            hit_tags.append(tag)
    # 路径 A'：英文问题 —— 英文别名映射回中文标签，再走同一套加权。
    # 不加这一步，英文问题命中 0 个标签，必然掉进 FALLBACK 的三个兜底专家。
    for alias, tags in EN_TAG_ALIASES.items():
        if alias in q_lower:
            for t in tags:
                if t in tag_index and t not in hit_tags:
                    hit_tags.append(t)
    for tag in hit_tags:
        for s in tag_index[tag]:
            if s in experts:
                add(s, "A")
    # 路径 B：口语兜底词表
    used_orals = []
    for word, slugs in ORAL_MAP.items():
        if word in q_lower:
            used_orals.append(word)
            for s in slugs:
                if s in experts:
                    add(s, "B")
    # 路径 C：domain slug 匹配 —— domain 字段本来就是英文（value-investing、
    # short-term-trading…），不需要给 345 个中文标签逐个做英文别名就能进组阁。
    # 规则是「domain 拆词后全部出现在问题里」，避免单词误命中（如 "trading" 单独出现不算）。
    q_words = {w for w in re.split(r"[^a-z0-9]+", q_lower) if w}
    for slug, e in experts.items():
        parts = [w for w in str(e.get("domain") or "").split("-") if w]
        if parts and all(w in q_words for w in parts):
            add(slug, "B")

    # 收敛排序
    def sort_key(slug):
        s = strength[slug]
        return (STAGE_ORDER[experts[slug]["stage"]], -(s[0] * 2 + s[1]), slug)

    ordered = sorted(strength, key=sort_key)

    # 阶段限额取正式席位
    formal = []
    per_stage = {"宏观定调": [], "中观筛选": [], "微观决策": []}
    for s in ordered:
        st = experts[s]["stage"]
        if len(per_stage[st]) < LIMITS[st]:
            per_stage[st].append(s)
    # 兜底：空阶段补位（且不在正式内）
    for st, fb in FALLBACK.items():
        if not per_stage[st] and fb not in sum(per_stage.values(), []):
            per_stage[st].append(fb)
            strength.setdefault(fb, [0, 0])

    # 情境补位：问题命中模式 -> 按序补位（限额未满才补）
    import re as _re
    for pattern, slugs in CONTEXT_RULES:
        if not _re.search(pattern, question, _re.IGNORECASE):
            continue
        for s in slugs:
            st = experts[s]["stage"]
            if s not in sum(per_stage.values(), []) and len(per_stage[st]) < LIMITS[st]:
                per_stage[st].append(s)
                strength.setdefault(s, [0, 0])
    formal = per_stage["宏观定调"] + per_stage["中观筛选"] + per_stage["微观决策"]

    # 列席：正式之外的命中者
    formal_set = set(formal)
    column = [s for s in ordered if s not in formal_set][:column]

    return {
        "question": question,
        "hit_tags": hit_tags,
        "oral_words": used_orals,
        "formal": formal,
        "column": column,
        "data_plan": [d for st in ("宏观定调", "中观筛选", "微观决策")
                      for d in (DATA_PLAN[st] if per_stage[st] else [])],
    }


def _label(slug, experts):
    e = experts[slug]
    code = e.get("code")
    return f"{slug} ({code}) {e['person']}" if code else f"{slug} {e['person']}"


def fmt(exp):
    m = load_matrix()
    e = m["experts"]
    lines = []
    lines.append(f"问题：{exp['question']}")
    lines.append(f"命中标签：{'、'.join(exp['hit_tags']) or '无（走口语词表）'}"
                 f"{' + 口语词：' + '、'.join(exp['oral_words']) if exp['oral_words'] else ''}")
    stage_title = {"宏观定调": "① 宏观定调", "中观筛选": "② 中观筛选", "微观决策": "③ 微观决策"}
    stage_seq = ["宏观定调", "中观筛选", "微观决策"]
    lines.append("\n正式席位：")
    for st in stage_seq:
        slugs = [s for s in exp["formal"] if e[s]["stage"] == st]
        if slugs:
            row = "  ".join(_label(s, e) for s in slugs)
            lines.append(f"  {stage_title[st]}：{row}")
    lines.append("\n列席备询：")
    if exp["column"]:
        row = "  ".join(_label(s, e) for s in exp["column"])
        lines.append("  " + row)
    else:
        lines.append("  （无）")
    lines.append("\n建议数据清单：")
    for d in exp["data_plan"]:
        lines.append(f"  - {d}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python assemble.py \"问题\" [--json]")
        sys.exit(1)
    q = sys.argv[1]
    result = assemble(q)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(fmt(result))
