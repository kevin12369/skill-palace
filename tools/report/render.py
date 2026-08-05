# -*- coding: utf-8 -*-
"""圆桌会议报告 HTML 渲染器 —— 风格化 v3（深色金融终端 / 实时数据驾驶舱）。

风格参考：https://www.valliance-ailab.com/ai-monetization-tracker/
- 深色终端：背景 #0A0A0F，卡片 #16161E，1px 极细描边 rgba(255,255,255,.06)，微弱深色阴影
- 数据发光：大数字（tabular-nums 等宽 + 粗体 + 明黄高亮），增量小字 + 涨跌胶囊 badge
- 品牌色区分阶段：宏观=蓝紫 #6366F1、中观=橙 #D97757、微观=绿 #10A37F
- 实时驾驶舱：KPI 大数字卡网格 + LIVE 徽标 + 编号区块标题
- 涨跌遵循中国惯例：涨红 #EF4444 / 跌绿 #10A37F
- 遵循 ardot-ui-design：Purpose First / Dominant Region / Density Intentionality / Constraint Over Decoration

接口：render_roundtable_html(data_dict) -> html str
新增可选字段：data["kpis"] = [{"label","value","delta","note","tone"}]  tone: neutral|ok|warn|bad
"""
import html as _html

# ═══════ CSS（深色驾驶舱 v3）═══════
CSS = """\
:root {
  --canvas: #0A0A0F;
  --card: #16161E;
  --card-2: #1B1B26;
  --line: rgba(255,255,255,.07);
  --line-strong: rgba(255,255,255,.14);
  --text: #F4F5F7;
  --text-2: #A6A8B8;
  --muted: #6E7180;
  --indigo: #6366F1;
  --indigo-soft: rgba(99,102,241,.15);
  --amber: #D97757;
  --amber-soft: rgba(217,119,87,.14);
  --green: #10A37F;
  --green-soft: rgba(16,163,127,.14);
  --red: #EF4444;
  --red-soft: rgba(239,68,68,.14);
  --yellow: #F5C518;
  --up: #EF4444;
  --down: #10A37F;
  --font: "Inter", -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
  --mono: "JetBrains Mono", "SF Mono", "Cascadia Code", Consolas, monospace;
  --radius: 14px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: var(--font); font-size: 14px; line-height: 1.65; color: var(--text); background: var(--canvas); padding: 40px 16px; background-image: radial-gradient(900px 380px at 70% -10%, rgba(99,102,241,.08), transparent 60%); }
.report { max-width: 940px; margin: 0 auto; background: var(--canvas); border: 1px solid var(--line); border-radius: 20px; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,.5); }

.header { padding: 40px 44px 30px; border-bottom: 1px solid var(--line); position: relative; }
.header-top { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.header-mark { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg,#6366F1,#10A37F); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px; color: #fff; box-shadow: 0 0 22px rgba(99,102,241,.45); }
.header-brand { font-size: 12px; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
.header-live { margin-left: auto; display: inline-flex; align-items: center; gap: 7px; font-family: var(--mono); font-size: 11px; color: var(--green); border: 1px solid rgba(16,163,127,.4); border-radius: 999px; padding: 3px 12px; }
.header-live::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); }
.header h1 { font-size: 28px; font-weight: 700; letter-spacing: -.01em; margin-bottom: 10px; }
.header-meta { display: flex; gap: 22px; flex-wrap: wrap; font-size: 12.5px; color: var(--text-2); }
.header-meta .meta-item { display: flex; align-items: center; gap: 6px; }
.header-meta .meta-item::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: var(--indigo); }

.section { padding: 30px 44px; border-bottom: 1px solid var(--line); }
.section:last-of-type { border-bottom: none; }
.section-head { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.section-no { font-family: var(--mono); font-size: 12px; font-weight: 700; color: var(--indigo); border: 1px solid var(--line-strong); border-radius: 8px; padding: 4px 10px; letter-spacing: .05em; }
.section-title { font-size: 17px; font-weight: 700; }
.section-sub { font-size: 12px; color: var(--muted); margin-left: auto; font-family: var(--mono); }

.lead { font-size: 13px; color: var(--text-2); margin-bottom: 18px; }
.lead strong { color: var(--yellow); font-weight: 600; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 6px; }
.kpi-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 18px; position: relative; overflow: hidden; }
.kpi-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--kpi, var(--indigo)), transparent 80%); }
.kpi-label { font-size: 11px; color: var(--muted); letter-spacing: .08em; margin-bottom: 8px; text-transform: uppercase; }
.kpi-value { font-family: var(--mono); font-size: 26px; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; }
.kpi-delta { font-size: 11.5px; margin-top: 7px; }
.kpi-delta .badge { font-family: var(--mono); padding: 1px 8px; border-radius: 6px; font-weight: 600; margin-right: 6px; }
.badge-ok { background: var(--green-soft); color: var(--green); }
.badge-warn { background: var(--amber-soft); color: var(--amber); }
.badge-bad { background: var(--red-soft); color: var(--red); }
.badge-neutral { background: rgba(255,255,255,.06); color: var(--text-2); }
.kpi-note { color: var(--muted); }

.assembly-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.assembly-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 18px; position: relative; overflow: hidden; }
.assembly-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.assembly-card.macro::before { background: linear-gradient(90deg,#6366F1,#8B5CF6); }
.assembly-card.meso::before { background: linear-gradient(90deg,#D97757,#F59E0B); }
.assembly-card.micro::before { background: linear-gradient(90deg,#10A37F,#34D399); }
.assembly-card h4 { font-size: 11.5px; color: var(--muted); font-weight: 600; letter-spacing: .1em; margin-bottom: 12px; }
.expert-row { display: flex; flex-direction: column; gap: 8px; }
.expert-pill { display: inline-flex; align-items: center; gap: 9px; font-size: 13px; font-weight: 500; color: var(--text); }
.expert-pill .code { font-family: var(--mono); font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 6px; letter-spacing: .03em; }
.code-blue { background: var(--indigo-soft); color: #A5B4FC; }
.code-amber { background: var(--amber-soft); color: var(--amber); }
.code-green { background: var(--green-soft); color: var(--green); }
.code-red { background: var(--red-soft); color: var(--red); }
.column-block { margin-top: 16px; padding-top: 14px; border-top: 1px dashed var(--line-strong); }
.column-label { font-size: 11px; color: var(--muted); letter-spacing: .1em; margin-bottom: 8px; }
.column-chips { display: flex; flex-wrap: wrap; gap: 7px; }
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 3px 11px; border-radius: 999px; font-size: 12px; background: var(--card-2); color: var(--text-2); border: 1px solid var(--line); }
.chip .code { font-family: var(--mono); font-size: 10.5px; font-weight: 700; color: var(--indigo); }

.mech-note { margin-top: 16px; padding: 12px 16px; border-radius: 10px; background: var(--card-2); border: 1px solid var(--line); font-size: 12px; color: var(--text-2); line-height: 1.6; }
.mech-note code { font-family: var(--mono); background: rgba(255,255,255,.05); border: 1px solid var(--line); padding: 1px 6px; border-radius: 5px; font-size: 11px; color: #A5B4FC; }

.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 12px 16px; font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--line); font-size: 11px; letter-spacing: .08em; }
.data-table td { padding: 11px 16px; border-bottom: 1px solid rgba(255,255,255,.04); font-variant-numeric: tabular-nums; }
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover { background: rgba(255,255,255,.02); }
.data-table .up { color: var(--up); font-weight: 600; }
.data-table .down { color: var(--down); font-weight: 600; }
.data-table .hl { font-weight: 700; color: var(--yellow); }
.data-table .hl-danger { font-weight: 700; color: var(--red); background: var(--red-soft); border-radius: 6px; padding: 1px 8px; }
.data-table .note { font-size: 12px; color: var(--muted); }
.data-table td.mono { font-family: var(--mono); }

.speech-list { display: flex; flex-direction: column; gap: 14px; }
.speech-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; transition: transform .12s, border-color .12s; }
.speech-card:hover { transform: translateY(-2px); border-color: var(--line-strong); }
.speech-head { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border-bottom: 1px solid var(--line); }
.avatar { width: 40px; height: 40px; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-family: var(--mono); font-size: 12.5px; font-weight: 800; color: #fff; letter-spacing: .02em; flex-shrink: 0; }
.avatar.macro { background: linear-gradient(135deg,#6366F1,#8B5CF6); box-shadow: 0 0 16px rgba(99,102,241,.4); }
.avatar.meso { background: linear-gradient(135deg,#D97757,#F59E0B); box-shadow: 0 0 16px rgba(217,119,87,.35); }
.avatar.micro { background: linear-gradient(135deg,#10A37F,#34D399); box-shadow: 0 0 16px rgba(16,163,127,.35); }
.speech-info { flex: 1; }
.speech-name { font-weight: 700; font-size: 14.5px; }
.speech-role { font-size: 12px; color: var(--muted); margin-top: 1px; }
.stage-tag { font-size: 11px; font-weight: 600; padding: 3px 12px; border-radius: 999px; white-space: nowrap; font-family: var(--mono); }
.stage-tag.macro { background: var(--indigo-soft); color: #A5B4FC; }
.stage-tag.meso { background: var(--amber-soft); color: var(--amber); }
.stage-tag.micro { background: var(--green-soft); color: var(--green); }
.stage-tag.decider { background: linear-gradient(135deg,#10A37F,#0D8A6C); color: #fff; }
.speech-body { padding: 18px 20px; font-size: 14px; line-height: 1.8; color: var(--text-2); }
.speech-body p + p { margin-top: 10px; }
.speech-body strong { color: var(--text); font-weight: 600; }
.speech-body blockquote { margin: 14px 0 2px; padding: 12px 18px; border-left: 3px solid var(--indigo); background: var(--indigo-soft); border-radius: 0 10px 10px 0; font-weight: 600; color: #D7D9F5; font-size: 14px; }

.check-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.check-box { border-radius: var(--radius); padding: 20px 22px; border: 1px solid var(--line); }
.check-box h4 { font-size: 12.5px; font-weight: 700; margin-bottom: 12px; letter-spacing: .05em; }
.check-box ul { padding-left: 18px; }
.check-box li { font-size: 13px; margin-bottom: 7px; line-height: 1.55; color: var(--text-2); }
.check-box.consensus { background: linear-gradient(160deg, rgba(16,163,127,.10), rgba(16,163,127,.02)); border-color: rgba(16,163,127,.35); }
.check-box.consensus h4 { color: var(--green); }
.check-box.divergence { background: linear-gradient(160deg, rgba(217,119,87,.10), rgba(217,119,87,.02)); border-color: rgba(217,119,87,.35); }
.check-box.divergence h4 { color: var(--amber); }

.verdict-wrap { background: linear-gradient(150deg, #101024 0%, #15152B 55%, #0E2030 100%); border: 1px solid rgba(99,102,241,.35); border-radius: var(--radius); padding: 28px 30px; position: relative; overflow: hidden; }
.verdict-wrap::after { content: ""; position: absolute; top: -60px; right: -40px; width: 220px; height: 220px; border-radius: 50%; background: radial-gradient(circle, rgba(99,102,241,.18), transparent 65%); pointer-events: none; }
.verdict-kicker { font-size: 11px; letter-spacing: .22em; text-transform: uppercase; color: #A5B4FC; margin-bottom: 10px; font-family: var(--mono); }
.verdict-title { font-size: 24px; font-weight: 800; margin-bottom: 20px; letter-spacing: -.01em; }
.verdict-points { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; position: relative; }
.verdict-point { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); border-radius: 12px; padding: 16px 18px; font-size: 13px; line-height: 1.6; color: var(--text-2); }
.verdict-point strong { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: #A5B4FC; margin-bottom: 6px; font-family: var(--mono); }
.verdict-oneline { text-align: center; font-size: 14px; font-weight: 600; color: var(--yellow); margin-top: 18px; }

.footer { padding: 22px 44px; border-top: 1px solid var(--line); font-size: 12px; color: var(--muted); background: #0C0C12; }
.footer p { margin-bottom: 4px; }
.footer code { font-family: var(--mono); color: var(--muted); }

@media (max-width: 760px) {
  body { padding: 0; }
  .report { border-radius: 0; }
  .header, .section, .footer { padding: 22px 20px; }
  .header h1 { font-size: 22px; }
  .kpi-grid, .assembly-grid, .check-grid, .verdict-points { grid-template-columns: 1fr 1fr; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) { .kpi-grid, .assembly-grid { grid-template-columns: 1fr; } }
"""

STAGE_CONFIG = {
    "宏观定调": {"no": "01", "cls": "macro", "code_cls": "code-blue", "avatar_cls": "avatar macro", "stage_cls": "stage-tag macro"},
    "中观筛选": {"no": "02", "cls": "meso",  "code_cls": "code-amber", "avatar_cls": "avatar meso",  "stage_cls": "stage-tag meso"},
    "微观决策": {"no": "03", "cls": "micro", "code_cls": "code-green", "avatar_cls": "avatar micro", "stage_cls": "stage-tag micro"},
}
KPI_TONE = {"ok": "badge-ok", "warn": "badge-warn", "bad": "badge-bad", "neutral": "badge-neutral"}


def render_roundtable_html(data):
    """data 结构同 v2；新增可选 data["kpis"]。"""
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>圆桌会议报告 · {_html.escape(data['question'])}</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="report">
{_render_header(data)}
{_render_kpis(data)}
{_render_assembly(data)}
{_render_data_table(data)}
{_render_speeches(data, "宏观定调")}
{_render_speeches(data, "中观筛选")}
{_render_speeches(data, "微观决策")}
{_render_cross_check(data)}
{_render_verdict(data)}
{_render_footer(data)}
</div>
</body>
</html>"""


def _render_header(data):
    return f"""\
<div class="header">
  <div class="header-top">
    <div class="header-mark">◆</div>
    <span class="header-brand">SKILL Palace · Roundtable</span>
    <span class="header-live">LIVE 实时组阁</span>
  </div>
  <h1>{_html.escape(data['question'])}</h1>
  <div class="header-meta">
    <span class="meta-item">📅 {_html.escape(data.get('date',''))}</span>
    <span class="meta-item">📊 {_html.escape(data.get('source',''))}</span>
    <span class="meta-item">🤖 {_html.escape(data.get('assembly_method','assemble.py 确定性组阁'))}</span>
  </div>
</div>"""


def _render_kpis(data):
    kpis = data.get("kpis")
    if not kpis:
        return ""
    cards = ""
    for k in kpis:
        badge = ""
        if k.get("delta"):
            tone = KPI_TONE.get(k.get("tone", "neutral"), "badge-neutral")
            badge = f'<span class="badge {tone}">{k["delta"]}</span>'
        color = {"ok": "var(--green)", "warn": "var(--amber)", "bad": "var(--red)", "neutral": "var(--text)"}.get(k.get("tone", "neutral"))
        note = f'<span class="kpi-note">{k.get("note","")}</span>' if k.get("note") else ""
        cards += f"""\
    <div class="kpi-card" style="--kpi:{color}">
      <div class="kpi-label">{k['label']}</div>
      <div class="kpi-value" style="color:{color}">{k['value']}</div>
      <div class="kpi-delta">{badge}{note}</div>
    </div>"""
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">●</span><span class="section-title">关键指标</span><span class="section-sub">{_html.escape(data.get('date',''))} · 实时</span></div>
  <div class="kpi-grid">{cards}</div>
</div>"""


def _render_assembly(data):
    a = data.get("assembly", {})
    cards = ""
    for stage_name, cfg in STAGE_CONFIG.items():
        experts = a.get("stages", {}).get(stage_name, [])
        if not experts:
            continue
        rows = "".join(
            f'<span class="expert-pill"><span class="code {cfg["code_cls"]}">{e["code"]}</span>{e["name"]}</span>'
            for e in experts
        )
        cards += f"""\
    <div class="assembly-card {cfg['cls']}">
      <h4>{stage_name}</h4>
      <div class="expert-row">{rows}</div>
    </div>"""
    col = ""
    if a.get("column"):
        chips = "".join(
            f'<span class="chip"><span class="code">{e["code"]}</span>{e["name"]}</span>'
            for e in a["column"]
        )
        col = f'<div class="column-block"><div class="column-label">列席备询</div><div class="column-chips">{chips}</div></div>'
    mech = ""
    if a.get("mech_note_html"):
        mech = f'<div class="mech-note">💡 {a["mech_note_html"]}</div>'
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">00</span><span class="section-title">动态组阁</span><span class="section-sub">{a.get('tags_hit','?')} 标签 / {a.get('candidates','?')} 候选 → {a.get('formal_count','?')} 席位</span></div>
  <p class="lead">问题解析 → 标签命中 → 三阶段收敛（宏观定调 → 中观筛选 → 微观决策），确定性组阁。</p>
  <div class="assembly-grid">{cards}</div>
  {col}
  {mech}
</div>"""


def _render_data_table(data):
    dt = data.get("data_table")
    if not dt:
        return ""
    th = "".join(f"<th>{h}</th>" for h in dt["headers"])
    trs = ""
    for row in dt["rows"]:
        tds = ""
        for cell in row:
            if isinstance(cell, dict):
                cls = cell.get("class", "")
                style = cell.get("style", "")
                tds += f'<td class="{cls}" style="{style}">{cell["v"]}</td>'
            else:
                tds += f"<td>{cell}</td>"
        trs += f"<tr>{tds}</tr>"
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">01</span><span class="section-title">数据锚点</span><span class="section-sub">{_html.escape(data.get('date',''))} 快照</span></div>
  <div class="table-wrap"><table class="data-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>
</div>"""


def _render_speeches(data, stage_name):
    speeches = [s for s in data.get("speeches", []) if s.get("stage") == stage_name]
    if not speeches:
        return ""
    cfg = STAGE_CONFIG[stage_name]
    cards = ""
    for s in speeches:
        decider = s.get("is_decider")
        tag_cls = "stage-tag decider" if decider else cfg["stage_cls"]
        tag_txt = (stage_name + " · 最终拍板") if decider else stage_name
        cards += f"""\
    <div class="speech-card">
      <div class="speech-head">
        <div class="{cfg['avatar_cls']}">{s['code']}</div>
        <div class="speech-info">
          <div class="speech-name">{s['name']}</div>
          <div class="speech-role">{s['role']}</div>
        </div>
        <span class="{tag_cls}">{tag_txt}</span>
      </div>
      <div class="speech-body">{s.get('content_html','')}</div>
    </div>"""
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">{cfg['no']}</span><span class="section-title">{stage_name}</span></div>
  <div class="speech-list">{cards}</div>
</div>"""


def _render_cross_check(data):
    cc = data.get("cross_check")
    if not cc:
        return ""
    con = "".join(f"<li>{i}</li>" for i in cc.get("consensus", []))
    div = "".join(f"<li>{i}</li>" for i in cc.get("divergence", []))
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">04</span><span class="section-title">交叉验证</span></div>
  <div class="check-grid">
    <div class="check-box consensus"><h4>✓ 共识</h4><ul>{con}</ul></div>
    <div class="check-box divergence"><h4>⚡ 分歧</h4><ul>{div}</ul></div>
  </div>
</div>"""


def _render_verdict(data):
    v = data.get("verdict")
    if not v:
        return ""
    pts = ""
    for p in v.get("points", []):
        pts += f'<div class="verdict-point"><strong>{p["label"]}</strong>{p["text"]}</div>'
    oneline = f'<div class="verdict-oneline">「{v.get("oneline","")}」</div>' if v.get("oneline") else ""
    return f"""\
<div class="section">
  <div class="section-head"><span class="section-no">05</span><span class="section-title">最终裁决</span></div>
  <div class="verdict-wrap">
    <div class="verdict-kicker">Final Verdict</div>
    <div class="verdict-title">{v.get('title','')}</div>
    <div class="verdict-points">{pts}</div>
  </div>
  {oneline}
</div>"""


def _render_footer(data):
    return f"""\
<div class="footer">
  <p><strong>⚠ 免责声明</strong>：{data.get('disclaimer', f'以上为圆桌框架推演，数据截至 {data.get("date","")} 快照，非投资建议。请以实时信息为准。')}</p>
  <p>{data.get('footer_html','本报告由 SKILL Palace 圆桌会议生成 · GitHub: kevin12369/skill-palace')}</p>
</div>"""
