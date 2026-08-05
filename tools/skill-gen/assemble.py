# -*- coding: utf-8 -*-
"""圆桌组阁执行脚本：输入问题文本 -> 正式席位 + 列席备询 + 建议数据清单。

用法：
    python assemble.py "当前A股能不能上车"
    python assemble.py "美联储降息对A股意味着什么" --json

设计要点（对应 ROUNDTABLE.md「组阁算法」）：
1. 两级命中：A) 问题 token 直接匹配 tag_index；B) 口语兜底词表（解决"能不能上车"类字面匹配弱）。
2. 确定性收敛：按 阶段顺序 -> 命中强度降序 -> 字母序 排序；阶段限额 宏观≤3/中观≤2/微观≤2。
3. 兜底规则：宏观空补 GS、中观空补 CM、微观空补 WB（保证三阶段齐全）。
4. 列席 = 正式之外的命中者，按序取 ≤6。
5. 建议数据清单：按正式席位阶段聚合。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAT = os.path.join(ROOT, "registry", "roundtable-matrix.json")

STAGE_ORDER = {"宏观定调": 0, "中观筛选": 1, "微观决策": 2}
LIMITS = {"宏观定调": 3, "中观筛选": 2, "微观决策": 2}
FALLBACK = {"宏观定调": "GS", "中观筛选": "CM", "微观决策": "WB"}
COLUMN_MAX = 6

# 口语兜底词表：高频问法/口语 -> 候选代码。值必须存在于 experts，脚本会防御性过滤。
ORAL_MAP = {
    "上车": ["DY", "QG", "WB", "PL"], "买入": ["DY", "QG", "WB", "PL"],
    "买不买": ["DY", "QG", "WB", "PL"], "该不该买": ["DY", "QG", "WB", "PL"],
    "值不值得买": ["DY", "QG", "WB", "PL"], "抄底": ["CM", "QG", "HOM"],
    "追高": ["CM", "HOM", "RS"], "泡沫": ["RS", "HOM", "GP", "SZ"], "崩盘": ["NT", "HM"],
    "风险": ["NT", "HOM", "CM"], "牛市": ["LD"], "熊市": ["LD"], "底部": ["LD", "HH"],
    "见顶": ["LD", "RS"], "牛熊": ["LD", "HH"], "降息": ["BB", "GP", "FP"],
    "加息": ["GP", "BB"], "美联储": ["GP", "BB"], "央行": ["BB", "FP"],
    "利率": ["FP", "GP", "BB"], "汇率": ["FP", "GP", "GS"], "流动性": ["HH", "BB", "FP"],
    "北向": ["HH"], "资金": ["HH"], "成长": ["PL", "PF"], "十倍": ["PL"],
    "科技": ["GT", "CP", "SP"], "ai": ["GT", "CP"], "芯片": ["GT"],
    "赛道": ["QG", "PF"], "龙头": ["QG", "WB"], "茅台": ["QG", "DY", "WB"],
    "银行": ["QG", "LD"], "消费": ["QG", "WB"], "财报": ["LS", "QG"], "财务": ["LS"],
    "审计": ["LS"], "治理": ["LS"], "估值": ["QG", "WB", "HH"], "贵": ["QG", "RS"],
    "便宜": ["QG", "DY", "WB"], "安全边际": ["WB", "DY", "CM"], "商业模式": ["DY", "WB"],
    "长期持有": ["DY", "WB", "PL"], "价值投资": ["WB", "DY", "QG"], "政策": ["LD", "GS", "BB"],
    "地产": ["GS", "LD"], "人口": ["GS"], "房地产": ["GS"], "通缩": ["IF", "BB"],
    "债务": ["IF", "RD", "HM"], "去杠杆": ["RD", "HM", "IF"], "信用": ["HH", "BB", "HM"],
    "衰退": ["RD", "IF"], "周期": ["HH", "KN", "HOM"], "康波": ["KN"], "长波": ["KN"],
    "不确定性": ["NT", "HOM"], "尾部": ["NT"], "反脆弱": ["NT"], "通胀": ["GP", "IF"],
    "非农": ["GP"], "补仓": ["QG", "WB", "DY"], "止损": ["CM", "NT"], "仓位": ["CE", "HOM", "CM"],
    "配置": ["CE", "RD", "BM"], "指数": ["BM", "CE"], "基金": ["BM", "CE"], "定投": ["BM", "CE"],
    "股市": ["LD", "HH", "GS"], "大盘": ["LD", "HH", "GS"], "行情": ["HH", "LD", "GS"],
    "走势": ["HH", "LD"], "经济": ["GS", "HH"], "追": ["RS", "HOM", "CM", "SZ"],
    "科创": ["RS", "HOM", "GT", "CP"], "还能涨吗": ["RS", "HOM"], "炒": ["RS", "HOM", "FS"],
}

# 情境补位规则：问题命中模式 -> 按序补位（限额未满才补；已满则进列席）。
# 解决"中国/A股问题缺宏观三人""科技泡沫问题缺泡沫专家"等字面命中的结构性盲区。
CONTEXT_RULES = [
    (r"A股|股市|大盘|中国", ["GS", "HH", "LD"]),
    (r"美联储|降息|加息|美元|全球|美元指数", ["GP", "BB", "FP"]),
    (r"科创|芯片|AI|科技|半导体", ["RS", "HOM", "GT", "SZ"]),
    (r"消费|白酒|食品|医药|家电", ["QG", "DY", "WB"]),
    (r"新能源|电池|光伏|储能|电动车", ["PL", "WR", "GT"]),
    (r"银行|保险|地产|红利|高股息", ["LD", "QG", "IF"]),
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
    strength = {}  # code -> (A命中数, B命中数)

    def add(code, kind):
        d = strength.setdefault(code, [0, 0])
        d[0 if kind == "A" else 1] += 1

    hit_tags = []
    # 路径 A：标签在问题中出现（忽略大小写子串）
    for tag, codes in tag_index.items():
        if tag.lower() in q_lower:
            hit_tags.append(tag)
            for c in codes:
                if c in experts:
                    add(c, "A")
    # 路径 B：口语兜底词表
    used_orals = []
    for word, codes in ORAL_MAP.items():
        if word in q_lower:
            used_orals.append(word)
            for c in codes:
                if c in experts:
                    add(c, "B")

    # 收敛排序
    def sort_key(code):
        s = strength[code]
        return (STAGE_ORDER[experts[code]["stage"]], -(s[0] * 2 + s[1]), code)

    ordered = sorted(strength, key=sort_key)

    # 阶段限额取正式席位
    formal = []
    per_stage = {"宏观定调": [], "中观筛选": [], "微观决策": []}
    for c in ordered:
        st = experts[c]["stage"]
        if len(per_stage[st]) < LIMITS[st]:
            per_stage[st].append(c)
    # 兜底：空阶段补位（且不在正式内）
    for st, fb in FALLBACK.items():
        if not per_stage[st] and fb not in sum(per_stage.values(), []):
            per_stage[st].append(fb)
            strength.setdefault(fb, [0, 0])

    # 情境补位：问题命中模式 -> 按序补位（限额未满才补）
    import re as _re
    for pattern, codes in CONTEXT_RULES:
        if not _re.search(pattern, question, _re.IGNORECASE):
            continue
        for c in codes:
            st = experts[c]["stage"]
            if c not in sum(per_stage.values(), []) and len(per_stage[st]) < LIMITS[st]:
                per_stage[st].append(c)
                strength.setdefault(c, [0, 0])
    formal = per_stage["宏观定调"] + per_stage["中观筛选"] + per_stage["微观决策"]

    # 列席：正式之外的命中者
    formal_set = set(formal)
    column = [c for c in ordered if c not in formal_set][:column]

    return {
        "question": question,
        "hit_tags": hit_tags,
        "oral_words": used_orals,
        "formal": formal,
        "column": column,
        "data_plan": [d for st in ("宏观定调", "中观筛选", "微观决策")
                      for d in (DATA_PLAN[st] if per_stage[st] else [])],
    }


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
        codes = [c for c in exp["formal"] if e[c]["stage"] == st]
        if codes:
            row = "  ".join(c + " " + e[c]["person"] for c in codes)
            lines.append(f"  {stage_title[st]}：{row}")
    lines.append("\n列席备询：")
    if exp["column"]:
        row = "  ".join(c + " " + e[c]["person"] for c in exp["column"])
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
