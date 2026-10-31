# -*- coding: utf-8 -*-
"""圆桌组阁回归：英文问题必须能召回，中文问题必须不退化。

为什么需要这个脚本
------------------
`assemble.py` 原本只做「中文标签 in 问题」的子串匹配。345 个标签里 330 个含中文，
所以任何英文问题都命中 0 个标签，最后必然落到 FALLBACK 的三个兜底专家——
英文用户拿到的圆桌永远是同一桌（gao-shanwen / charlie-munger / warren-buffett）。
这不是"效果差"，是"恒定不变"，属于功能性缺陷而非调参问题。

本脚本固定两件事：
1. 英文问题能命中标签，且正式席位里至少有一位不是兜底专家；
2. 纯中文问题不受英文通道影响（hit_tags 必须等于「纯中文子串匹配」的结果）——
   即加了英文别名之后，中文用户看到的组阁结果不能变。

用法：
    python scripts/check_roundtable_en.py
退出码 0 = 通过；1 = 有回归。
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "skill-gen"))

import assemble as A  # noqa: E402


# 英文问题 -> 至少应该命中其中的哪些标签（用于验证别名表真的生效）
EN_CASES: list[tuple[str, list[str]]] = [
    ("is NVDA in a bubble right now", ["泡沫"]),
    ("how do I size my position and set a stop loss", ["止损"]),
    ("does value investing still work", ["价值投资"]),
    ("what does the Fed cutting rates mean for A-share market", ["美联储", "A股"]),
    ("is the market sentiment too euphoric", ["市场情绪"]),
    ("should I use a moving average or MACD for entry", ["均线", "MACD"]),
    ("how to build a margin of safety into valuation", ["安全边际", "估值"]),
    ("where is support and resistance on the index", ["支撑阻力"]),
    ("global macro liquidity cycle and debt cycle", ["流动性", "债务周期"]),
    ("day trading discipline and risk management", ["短线交易", "风险控制"]),
]

# 纯中文问题：加了英文通道后结果不得变化
ZH_CASES: list[str] = [
    "当前A股能不能上车",
    "美联储降息对A股意味着什么",
    "怎么给仓位设置止损",
    "现在市场情绪是不是过热",
    "价值投资还管用吗",
]

FALLBACK_SLUGS = set(A.FALLBACK.values())


def main() -> int:
    matrix = A.load_matrix()
    tag_index = matrix["tag_index"]
    failures: list[str] = []

    # ---------- 1. 英文问题必须召回 ----------
    print("【英文问题】")
    for q, must_tags in EN_CASES:
        exp = A.assemble(q)
        hits = set(exp["hit_tags"])
        formal = exp["formal"]
        non_fallback = [s for s in formal if s not in FALLBACK_SLUGS]
        miss = [t for t in must_tags if t not in hits]
        ok = not miss and len(formal) >= 2 and non_fallback
        print(f"  {'✅' if ok else '❌'} {q}")
        print(f"      命中标签：{'、'.join(exp['hit_tags']) or '无'}"
              f"  正式席位 {len(formal)} 人（非兜底 {len(non_fallback)} 人）")
        if miss:
            failures.append(f"[EN] {q} → 未命中预期标签 {miss}")
        if len(formal) < 2:
            failures.append(f"[EN] {q} → 正式席位只有 {len(formal)} 人")
        if not non_fallback:
            failures.append(f"[EN] {q} → 正式席位全是兜底专家（组阁失效）")

    # ---------- 2. 中文问题不得退化 ----------
    print("\n【中文问题：不得因英文通道而改变】")
    for q in ZH_CASES:
        exp = A.assemble(q)
        q_lower = q.lower()
        # 纯中文子串匹配的期望结果（不做任何别名/domain 扩展）
        expected = {t for t in tag_index if t.lower() in q_lower}
        got = set(exp["hit_tags"])
        ok = got == expected
        print(f"  {'✅' if ok else '❌'} {q}  命中 {len(got)} 个标签")
        if not ok:
            extra = got - expected
            lost = expected - got
            failures.append(f"[ZH] {q} → 多出 {sorted(extra)} / 丢失 {sorted(lost)}")

    # ---------- 3. 兜底路径仍然可用 ----------
    print("\n【兜底：完全无关的问题仍应给出三阶段齐全的席位】")
    exp = A.assemble("zzz qqq xxx")
    stages = {A.load_matrix()["experts"][s]["stage"] for s in exp["formal"]}
    ok = stages == {"宏观定调", "中观筛选", "微观决策"}
    print(f"  {'✅' if ok else '❌'} 无关问题 → 阶段 {sorted(stages)}")
    if not ok:
        failures.append(f"[FALLBACK] 三阶段不全：{sorted(stages)}")

    print()
    if failures:
        print(f"回归失败：{len(failures)} 项")
        for f in failures:
            print("  -", f)
        return 1
    print("全部通过 ✅（英文可召回、中文无退化、兜底仍完整）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
