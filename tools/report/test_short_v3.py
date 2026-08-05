# 短线操作议题 -> v3 深色报告
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from render import render_roundtable_html

data = {
    "question": "当前 A 股适合短线操作么？（错过昨天·今天观望·没追高）",
    "date": "2026-08-05 收盘",
    "source": "westock 实时行情",
    "assembly_method": "assemble.py v2.2 (A股+短线+错过/观望词表)",
    "kpis": [
        {"label":"上证指数","value":"3,878","delta":"+1.47%","tone":"ok","note":"反弹，趋势未转"},
        {"label":"沪深300 PE","value":"14.3","delta":"历史偏低","tone":"ok","note":"价值区间"},
        {"label":"科创50 PE","value":"202.65","delta":"+4.78%","tone":"bad","note":"暴力反弹·极高风险"},
        {"label":"量能","value":"约1.05","delta":"未放量","tone":"warn","note":"反弹缺弹药验证"},
    ],
    "assembly": {
        "tags_hit": 2, "candidates": 18, "formal_count": 6, "column_count": 6,
        "stages": {
            "宏观定调": [{"code":"LD","name":"李大霄"},{"code":"RS","name":"席勒"},{"code":"SZ","name":"索罗斯"}],
            "中观筛选": [{"code":"BC","name":"北京炒家"},{"code":"CM","name":"芒格"}],
            "微观决策": [{"code":"DY","name":"段永平"},{"code":"PL","name":"林奇"}]
        },
        "column": [{"code":"XX","name":"徐翔(核心)"},{"code":"HOM","name":"马克斯"},{"code":"CE","name":"埃利斯"},{"code":"QG","name":"邱国鹭"},{"code":"WB","name":"巴菲特"}],
        "mech_note_html": '命中标签 A股 + 口语词「买入/追高/追/短线/错过/观望」+ 情境补位 RS/SZ。XX 徐翔因中观额度已满列入列席核心发言。'
    },
    "data_table": {
        "headers": ["标的","现价","当日","PE","5日","20日","60日","短线信号"],
        "rows": [
            ["上证指数","3,878",{"v":"+1.47%","class":"up"},"17.84",{"v":"+1.3%","class":"up"},{"v":"-2.33%","class":"down"},{"v":"-7.97%","class":"down"},"反弹，趋势未转"],
            ["<strong>沪深300</strong>","4,658",{"v":"+1.24%","class":"up"},{"v":"14.3","class":"hl"},{"v":"+1.26%","class":"up"},{"v":"-2.05%","class":"down"},{"v":"-5.86%","class":"down"},"短期通道"],
            ["创业板指","3,535",{"v":"+1.32%","class":"up"},"61.56",{"v":"+4.63%","class":"up"},{"v":"-8.07%","class":"down"},{"v":"-10.16%","class":"down"},"反弹+高波动"],
            ["科创50","1,694",{"v":"+4.78%","class":"up"},{"v":"202.65","class":"hl-danger"},{"v":"+0.89%","class":"up"},{"v":"-16%","class":"down"},{"v":"-1.75%","class":"down"},"暴力反弹·极高风险"],
            ["量能","—","比率≈1","—","—","—","—","未放量·缺弹药"],
        ]
    },
    "speeches": [
        {"stage":"宏观定调","code":"LD","name":"李大霄","role":"A股市场整体判断者","content_html":'<p>A 股整体看——上证 3,878、沪深300 14.3 倍 PE，底部区域特征仍在。今天反弹是冰点后的<strong>技术修复，不是反转确认</strong>。量能不够（约1），别被涨幅带偏。</p><blockquote>短线可以做但仓位要轻——底部区域买好股，别在反弹里追题材。</blockquote>'},
        {"stage":"宏观定调","code":"RS","name":"罗伯特·席勒","role":"行为泡沫与叙事经济学剖析者","content_html":'<p>科创50 PE <strong>202.65</strong>，今天 +4.78%。这是典型的<strong>"叙事驱动反弹"</strong>——AI 主题情绪的短期脉冲。20日 -16%、PE 200+，做短线相当于在火山口跳舞。</p><blockquote>短线最危险的幻觉就是"反弹了=错过了"——其实 PE 200 的反弹是刀口舔血。</blockquote>'},
        {"stage":"宏观定调","code":"SZ","name":"乔治·索罗斯","role":"反身性理论家与泡沫剖析者","content_html":'<p>"今天反弹 + 昨天没买 + 今天观望"——这就是反身性模型里<strong>"焦虑—追高—套牢"链条的起点</strong>。繁荣-萧条定位：市场从悲观冰点反弹 → FOMO 刚开始积累 → 你"看涨了觉得错过了"→ 这正是最容易追进去的时刻。</p><blockquote>短线的敌人不是错过昨天的买入，是因为"怕错过"而在错误信号下追高。</blockquote>'},
        {"stage":"中观筛选","code":"BC","name":"北京炒家","role":"题材博弈与龙头战法分析师","content_html":'<p>短线能不能做看三样——①<strong>主线题材</strong>：AI/科创今天主力，题材成立 ✓；②<strong>涨停板质量</strong>：要看首板/二板封板强度，今天部分尾盘松动；③<strong>量能</strong>：成交量比率约1，<strong>没放量</strong>——这是最大扣分项 ✗。</p><p>"错过昨天不是问题——短线没有"错过"这个词，只有"信号到了没"。今天板不够硬、量不够大，<strong>观望是对的</strong>。如果明天放量+龙头继续强→打板信号确认可小试。如果缩量→继续看。</p><blockquote>打最硬的板、等最稳的信号、割最快的肉。</blockquote>'},
        {"stage":"中观筛选","code":"CM","name":"查理·芒格","role":"首席逆向质疑者","content_html":'<p>把问题倒过来——<strong>"怎样在今天这个反弹里亏钱？"</strong>追高（错过焦虑驱动）、不设止损、买科创50 这种 PE 200 的题材、仓位太重。</p><p>你"观望没追高"，恰恰避开了 Lollapalooza 效应里最危险的一环：<strong>"反弹 × 错过焦虑 × 从众"的正反馈共振</strong>。</p><blockquote>热点题材进 Too Hard 筐，等信号确认再出手。</blockquote>'},
        {"stage":"微观决策","code":"XX","name":"徐翔","role":"短线交易策略与情绪分析师","content_html":'<p>"适不适合短线操作"看<strong>三信号是否共振</strong>：① <strong>资金面</strong>——量能约1，未放量，扣分；② <strong>技术面</strong>——上证突破前高但 60日 -7.97% 趋势未转，中性；③ <strong>消息/题材</strong>——AI/科创主力，加分。</p><p><strong>三信号只满足了 1.5 个：题材在，量不足，趋势未转。</strong>短线不是满仓信号——小仓位试龙头可以，但绝不追高、必须设 -3% 硬止损。错过昨天不追，纪律到位。</p><blockquote>信号不全就不做——量不来就等量来。</blockquote>'},
        {"stage":"微观决策","code":"DY","name":"段永平","role":"中国价值投资与企业质量评估师","is_decider":True,"content_html":'<p>短线不在我能力圈——<strong>不懂不做</strong>。"错过"不是问题，买公司不是买股价。看得懂的生意跌了是好事，涨了也不急着追。</p><blockquote>把"上车"当"买公司"而不是"赌行情"——做对的事情，不做短线的投机博弈。</blockquote>'},
    ],
    "cross_check": {
        "consensus": [
            "今天是反弹而非反转——量不足+趋势未转",
            '"错过不追高·观望是对的"是短线纪律的核心',
            "科创50 PE 202 的反弹是高风险赌博",
            "有题材但缺弹药，信号不完整，不宜重仓"
        ],
        "divergence": [
            'BC 认为"明天放量+题材延续可小试" vs CM/XX 更强调等完整信号',
            "DY 认为短线非能力圈，直接 pass",
            "HOM/CE 一致主张等分歧日低吸比今天追高胜率高"
        ]
    },
    "verdict": {
        "title": "短线今天不适合重仓——观望不追高是完全正确的纪律",
        "points": [
            {"label":"信号状态","text":"三信号只有题材一项到位（AI/科创领涨）。量不足+趋势未转，反弹缺弹药验证——不是凯旋信号。"},
            {"label":"你的操作","text":"错过昨天=不亏钱；今天观望不追=纪律到位。短线最贵的不是错过，是信号不全时追高。"},
            {"label":"明天如果","text":"放量(≥1.5)+题材延续+龙头首板/二板封死→可小仓位试龙头(-3%硬止损)；缩量+题材轮动→继续等分歧日低吸。"},
        ],
        "oneline": "打最硬的板、等最稳的信号、割最快的肉——反弹不是反转，观望不亏钱。"
    },
}

html = render_roundtable_html(data)
path = os.path.join(os.path.dirname(__file__), "demo_短线操作_v3.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated: {path}")
print(f"HTML length: {len(html)}")
