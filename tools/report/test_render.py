# 测试渲染器：A股上车 数据 → HTML
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.join(os.path.dirname(__file__), "tools/report")))
from render import render_roundtable_html

data = {
    "question": "当前 A 股能不能上车？",
    "date": "2026-08-05",
    "source": "westock 实时行情",
    "assembly": {
        "tags_hit": 25,
        "candidates": 15,
        "formal_count": 6,
        "column_count": 6,
        "stages": {
            "宏观定调": [{"code":"GS","name":"高善文"},{"code":"LD","name":"李大霄"},{"code":"HH","name":"洪灏"}],
            "中观筛选": [{"code":"CM","name":"查理·芒格"}],
            "微观决策": [{"code":"DY","name":"段永平"},{"code":"PL","name":"彼得·林奇"}]
        },
        "column": [{"code":"QG","name":"邱国鹭"},{"code":"WB","name":"巴菲特"},{"code":"FP","name":"付鹏"},{"code":"RS","name":"席勒"},{"code":"HOM","name":"马克斯"},{"code":"NT","name":"塔勒布"}],
        "mech_note_html": "本次组阁由 <code>tools/skill-gen/assemble.py</code> 脚本产出，全程确定性（两级命中 → 阶段限额 → 兜底 → 情境补位 → 列席）。主持人未做人工微调，脚本输出即与人工判断完全一致。"
    },
    "data_table": {
        "headers": ["标的","现价","当日","PE","YTD","60日","备注"],
        "rows": [
            ["上证指数","3,842",{"v":"+0.52%","class":"up"},"17.68",{"v":"-3.19%","class":"down"},{"v":"-8.83%","class":"down"},"20日 -3.24%"],
            ["<strong>沪深300</strong>","4,613",{"v":"+0.26%","class":"up"},{"v":"14.19","class":"highlight"},{"v":"-0.36%","class":"down"},{"v":"-6.77%","class":"down"},"历史偏低区 ★"],
            ["创业板指","3,496",{"v":"+0.19%","class":"up"},"60.83",{"v":"+9.13%","class":"up"},{"v":"-11.17%","class":"down"},"估值偏高"],
            ["科创50","1,668",{"v":"+3.21%","class":"up"},{"v":"200.58","class":"highlight"},{"v":"+24.1%","class":"up"},{"v":"-3.23%","class":"down"},"20日 -17.26% ⚠"],
            ["贵州茅台","1,311",{"v":"-1.33%","class":"down"},"19.81",{"v":"-2.85%","class":"down"},{"v":"-1.2%","class":"down"},"股息 3.97%"],
            ["宁德时代","402",{"v":"+1.86%","class":"up"},"21.91",{"v":"+11.68%","class":"up"},{"v":"-6.68%","class":"down"},"&mdash;"],
            ["腾讯控股","486",{"v":"-0.41%","class":"down"},"16.58",{"v":"-18.21%","class":"down"},{"v":"+4.18%","class":"up"},"便宜"],
            ["长江电力","27.8",{"v":"-1.87%","class":"down"},"18.83",{"v":"+6.03%","class":"up"},{"v":"+5.79%","class":"up"},"股息 3.6%"],
        ]
    },
    "speeches": [
        {"stage":"宏观定调","code":"GS","name":"高善文","role":"中国宏观背景提供者","content_html":'<p>用河床与水位框架——盈利的河床在磨底，但水位（流动性+风险偏好）仍被房地产与通缩预期压着。沪深300 14.19 倍是历史偏低区，整体是<strong>"河床上的价值"</strong>；麻烦在结构：科创50 200 倍、创业板 60 倍，资金在主题上单边押注。</p><blockquote>中国不是不能投，是缺一个把水位抬起来的信用扩张+信心修复的催化。在此之前是价值区间，不是趋势区间。</blockquote>'},
        {"stage":"宏观定调","code":"LD","name":"李大霄","role":"A股市场整体判断者","content_html":'<p>四维定位——政策暖风、估值低位（沪深300 14.19）、情绪冰点（60日 -8.83% 退潮）、资金待回流——这是典型的<strong>底部区域特征，钻石底附近</strong>。但要提醒：科创50 200 倍 PE 是"地球顶"级别的局部泡沫。</p><blockquote>大盘处于底部区域的上车区，但要买好股（低估值蓝筹），别在热点上追高。</blockquote>'},
        {"stage":"宏观定调","code":"HH","name":"洪灏","role":"宏观策略与周期定位分析师","content_html":"<p>信用周期仍在收缩后段，流动性拐点未确认；估值均值回归的引力向上——14.19 的沪深300 偏离中枢下方，但回归的<strong>时间不确定</strong>。北向与资金流未给出右侧信号。</p><blockquote>估值分位支持分批布局，但右侧确认前别一把梭。</blockquote>"},
        {"stage":"中观筛选","code":"CM","name":"查理·芒格","role":"首席逆向质疑者","content_html":'<p>把问题倒过来——<strong>怎样在 A 股亏光？</strong>追 PE 200 的科创50、上杠杆、买看不懂的题材、情绪化追涨杀跌。当前最大的 Lollapalooza 是 <strong>结构性狂热</strong>：科创50 YTD +24% 但 20日 -17%，是赌博不是价值。</p><p>反过来看，整体悲观+低估值+政策呵护符合逆向布局特征。但两边都别用"全仓"这个词。</p><blockquote>热点题材进 Too Hard 筐，看得懂的低估蓝筹进 Yes 筐。</blockquote>'},
        {"stage":"微观决策","code":"DY","name":"段永平","role":"中国价值投资与企业质量评估师","is_decider":True,"content_html":'<p>"能不能上车"先问<strong>"买什么生意"</strong>。茅台 PE 19.81、长电 18.83、宁德 21.91、腾讯 16.58——看得懂的商业模式都不贵甚至便宜；科创50 200 倍的东西，看不懂，不做。</p><blockquote>能上车，但上的是"价值车"不是"行情车"——买看得懂的好公司、分笔建仓、长期持有、不加杠杆，把"上车"当"买公司"而不是"赌行情"。</blockquote>'},
        {"stage":"微观决策","code":"PL","name":"彼得·林奇","role":"成长股识别与选股实操派","content_html":"<p>成长机会在 PEG 合理的公司（宁德 PE 21.91 与增速匹配），PEG&gt;2 的热门别碰；生活经验选股在 A 股同样适用，但需警惕创业板 60日 -11% 的波动。</p>"},
    ],
    "cross_check": {
        "consensus": ["整体估值不贵：沪深300 PE 14.19 处于历史偏低区","科创50 PE≈200 是共识雷区，六方一致回避","情绪冰点 + 政策呵护 = 逆向布局窗口","都主张分批建仓 + 留足现金，反对一把梭"],
        "divergence": ["LD 偏乐观（底部可上车） vs HH 偏谨慎（等信用右侧确认）","GS 看'等催化' vs QG/DY 认为价值区间即可分批","DY/QG 重个股轻择时 vs LD/HH 重市场位置"]
    },
    "verdict": {
        "title": '能上车——上"价值车"，不上"行情车"',
        "points": [
            {"label":"✅ 怎么上","text":"沪深300 类低估值蓝筹（PE 14.19、情绪冰点、政策呵护），分 3–4 笔逢低布局。逆向 + 便宜是硬道理。"},
            {"label":"❌ 怎么不上","text":"科创50（PE 200.58）结构性泡沫区，地球顶 / Too Hard 筐，坚决不追。"},
            {"label":"🛡 纪律","text":"留足现金、不加杠杆、以\"买公司\"而非\"赌行情\"的心态；待信用扩张/流动性右侧确认后再加码。"},
        ],
        "oneline": "一句话：别人在热点上贪婪，你该在冰点的便宜货上冷静——买看得懂的好公司，分批上车。"
    },
}

html = render_roundtable_html(data)
out = os.path.join(os.path.dirname(__file__), "demo_render_test.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated: {out}")
print(f"HTML length: {len(html)}")
