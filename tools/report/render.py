# -*- coding: utf-8 -*-
"""圆桌会议报告 HTML 渲染器 —— 风格化 v2。

设计原则（ardot-ui-design / guidelines-web-app）：
- Purpose First：一屏一焦点，报告主线 = 议题 → 组阁 → 数据 → 发言 → 裁决
- Dominant Region：裁决区是全页最强视觉焦点（深色大卡）
- Progressive Disclosure：组阁/数据/发言/验证/裁决 分段叙事
- Density Intentionality：报告页取 Airy 密度，数据表取 Compact
- Spatial Logic：单一纵向主轴，卡片化分区，空白即分隔
- Constraint Over Decoration：一切样式服务阅读层次与决策，不做纯装饰

接口与 v1 完全一致：render_roundtable_html(data_dict) -> html str
"""
import html as _html

# ═══════ CSS（风格化 v2）═══════
CSS = """\
:root {
  --ink: #0F1B2D;
  --ink-soft: #3E4C5F;
  --muted: #7A8699;
  --line: #E3E8F0;
  --paper: #FFFFFF;
  --canvas: #EEF2F7;
  --navy: #0B2A4A;
  --navy-2: #133B6B;
  --blue: #2563EB;
  --blue-soft: #E8F0FE;
  --amber: #D97706;
  --amber-soft: #FEF3E2;
  --green: #15803D;
  --green-soft: #E7F6EC;
  --red: #DC2626;
  --red-soft: #FDECEC;
  --up: #D85A30;
  --down: #15803D;
  --font: "Inter", -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
  --mono: "JetBrains Mono", "SF Mono", "Cascadia Code", Consolas, monospace;
  --radius: 14px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: var(--font); font-size: 14px; line-height: 1.65; color: var(--ink); background: var(--canvas); padding: 40px 16px; }
.report { max-width: 920px; margin: 0 auto; background: var(--paper); border-radius: 20px; box-shadow: 0 12px 40px rgba(11,42,74,.10); overflow: hidden; }

.header {
  position: relative;
  background: radial-gradient(1200px 400px at 85% -10%, rgba(37,99,235,.35), transparent 60%),
              linear-gradient(150deg, var(--navy) 0%, var(--navy-2) 70%, #1B4B8F 100%);
  color: #fff; padding: 44px 44px 36px; overflow: hidden;
}
.header::after {
  content: ""; position: absolute; inset: 0; opacity: .08;
  background-image: linear-gradient(rgba(255,255,255,.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.4) 1px, transparent 1px);
  background-size: 26px 26px; pointer-events: none;
}
.header-top { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.header-mark { width: 34px; height: 34px; border-radius: 9px; background: linear-gradient(135deg,#60A5FA,#2563EB); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; box-shadow: 0 4px 12px rgba(37,99,235,.4); }
.header-brand { font-size: 12px; letter-spacing: .18em; text-transform: uppercase; opacity: .75; }
.header h1 { font-size: 30px; font-weight: 700; letter-spacing: -.01em; margin-bottom: 12px; line-height: 1.25; }
.header-meta { display: flex; gap: 22px; flex-wrap: wrap; font-size: 12.5px; opacity: .85; position: relative; }
.header-meta .meta-item { display: flex; align-items: center; gap: 6px; }
.header-meta .meta-item::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: #60A5FA; }

.section { padding: 34px 44px; border-bottom: 1px solid var(--line); }
.section:last-of-type { border-bottom: none; }
.section-head { display: flex; align-items: baseline; gap: 14px; margin-bottom: 22px; }
.section-no { font-family: var(--mono); font-size: 26px; font-weight: 700; line-height: 1; color: #C9D4E4; }
.section-title { font-size: 18px; font-weight: 700; color: var(--ink); letter-spacing: -.01em; }
.section-sub { font-size: 12px; color: var(--muted); margin-left: auto; text-align: right; }

.lead { font-size: 13.5px; color: var(--ink-soft); margin-bottom: 18px; }
.lead strong { color: var(--navy); font-weight: 600; }

.assembly-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.assembly-card { border-radius: var(--radius); border: 1px solid var(--line); padding: 16px 18px; position: relative; overflow: hidden; background: #FBFCFE; }
.assembly-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.assembly-card.macro::before { background: linear-gradient(90deg,#2563EB,#60A5FA); }
.assembly-card.meso::before { background: linear-gradient(90deg,#D97706,#F5B04C); }
.assembly-card.micro::before { background: linear-gradient(90deg,#15803D,#4ADE80); }
.assembly-card h4 { font-size: 12px; color: var(--muted); font-weight: 600; letter-spacing: .06em; margin-bottom: 12px; }
.expert-row { display: flex; flex-direction: column; gap: 7px; }
.expert-pill { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; color: var(--ink); }
.expert-pill .code { font-family: var(--mono); font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 6px; letter-spacing: .03em; }
.code-blue { background: var(--blue-soft); color: var(--blue); }
.code-amber { background: var(--amber-soft); color: var(--amber); }
.code-green { background: var(--green-soft); color: var(--green); }
.code-red { background: var(--red-soft); color: var(--red); }
.column-block { margin-top: 16px; padding-top: 14px; border-top: 1px dashed var(--line); }
.column-label { font-size: 11.5px; color: var(--muted); letter-spacing: .08em; margin-bottom: 8px; }
.column-chips { display: flex; flex-wrap: wrap; gap: 7px; }
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 3px 11px; border-radius: 999px; font-size: 12px; background: var(--canvas); color: var(--ink-soft); border: 1px solid var(--line); }
.chip .code { font-family: var(--mono); font-size: 10.5px; font-weight: 700; }

.mech-note { margin-top: 16px; padding: 12px 16px; border-radius: 10px; background: #F6F8FC; border: 1px solid var(--line); font-size: 12px; color: var(--muted); line-height: 1.6; }
.mech-note code { font-family: var(--mono); background: #fff; border: 1px solid var(--line); padding: 1px 6px; border-radius: 5px; font-size: 11px; color: var(--navy); }

.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: var(--radius); }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 12px 14px; font-weight: 600; color: var(--muted); background: #F6F8FC; border-bottom: 1px solid var(--line); font-size: 11.5px; letter-spacing: .05em; }
.data-table td { padding: 11px 14px; border-bottom: 1px solid #EFF2F7; font-variant-numeric: tabular-nums; }
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:nth-child(even) { background: #FAFBFD; }
.data-table td.num { text-align: right; font-family: var(--mono); }
.data-table .up { color: var(--up); font-weight: 600; }
.data-table .down { color: var(--down); font-weight: 600; }
.data-table .hl { font-weight: 700; background: var(--amber-soft); border-radius: 5px; padding: 1px 7px; }
.data-table .hl-danger { font-weight: 700; background: var(--red-soft); color: var(--red); border-radius: 5px; padding: 1px 7px; }
.data-table .note { font-size: 12px; color: var(--muted); }

.speech-list { display: flex; flex-direction: column; gap: 16px; }
.speech-card { border-radius: var(--radius); border: 1px solid var(--line); overflow: hidden; background: #fff; transition: box-shadow .15s; }
.speech-card:hover { box-shadow: 0 6px 18px rgba(11,42,74,.08); }
.speech-head { display: flex; align-items: center; gap: 14px; padding: 16px 20px; background: #FBFCFE; border-bottom: 1px solid var(--line); }
.avatar { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-family: var(--mono); font-size: 13px; font-weight: 800; color: #fff; letter-spacing: .02em; flex-shrink: 0; }
.avatar.macro { background: linear-gradient(135deg,#2563EB,#60A5FA); }
.avatar.meso { background: linear-gradient(135deg,#D97706,#F5B04C); }
.avatar.micro { background: linear-gradient(135deg,#15803D,#4ADE80); }
.speech-info { flex: 1; }
.speech-name { font-weight: 700; font-size: 14.5px; }
.speech-role { font-size: 12px; color: var(--muted); margin-top: 1px; }
.stage-tag { font-size: 11px; font-weight: 600; padding: 3px 12px; border-radius: 999px; white-space: nowrap; }
.stage-tag.macro { background: var(--blue-soft); color: var(--blue); }
.stage-tag.meso { background: var(--amber-soft); color: var(--amber); }
.stage-tag.micro { background: var(--green-soft); color: var(--green); }
.stage-tag.decider { background: linear-gradient(135deg,#15803D,#16A34A); color: #fff; }
.speech-body { padding: 18px 20px; font-size: 14px; line-height: 1.8; color: var(--ink-soft); }
.speech-body p + p { margin-top: 10px; }
.speech-body strong { color: var(--ink); font-weight: 600; }
.speech-body blockquote { margin: 14px 0 2px; padding: 12px 18px; border-left: 3px solid var(--blue); background: var(--blue-soft); border-radius: 0 10px 10px 0; font-weight: 600; color: var(--navy); font-size: 14px; }

.check-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.check-box { border-radius: var(--radius); padding: 20px 22px; }
.check-box h4 { font-size: 13px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 7px; }
.check-box ul { padding-left: 18px; }
.check-box li { font-size: 13px; margin-bottom: 7px; line-height: 1.55; }
.check-box.consensus { background: linear-gradient(160deg, var(--green-soft), #F1FAF4); border: 1px solid #BFE3CB; }
.check-box.consensus h4 { color: var(--green); }
.check-box.divergence { background: linear-gradient(160deg, var(--amber-soft), #FFF9EC); border: 1px solid #F3D9A7; }
.check-box.divergence h4 { color: var(--amber); }

.verdict-wrap { background: linear-gradient(155deg, #0B2A4A 0%, #123B6B 55%, #1B4B8F 100%); border-radius: var(--radius); padding: 30px 32px; color: #fff; position: relative; overflow: hidden; }
.verdict-wrap::after { content: ""; position: absolute; inset: 0; opacity: .07; background-image: radial-gradient(circle at 90% 0%, #fff 1.5px, transparent 1.5px); background-size: 20px 20px; pointer-events: none; }
.verdict-kicker { font-size: 11px; letter-spacing: .2em; text-transform: uppercase; color: #93C5FD; margin-bottom: 10px; }
.verdict-title { font-size: 24px; font-weight: 700; margin-bottom: 20px; letter-spacing: -.01em; }
.verdict-points { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.verdict-point { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16); border-radius: 12px; padding: 16px 18px; font-size: 13px; line-height: 1.6; backdrop-filter: blur(2px); }
.verdict-point strong { display: block; font-size: 11.5px; text-transform: uppercase; letter-spacing: .1em; color: #93C5FD; margin-bottom: 6px; }
.verdict-oneline { text-align: center; font-size: 14px; font-weight: 600; color: var(--ink); margin-top: 18px; }

.footer { padding: 24px 44px; background: #F6F8FC; border-top: 1px solid var(--line); font-size: 12px; color: var(--muted); }
.footer p { margin-bottom: 4px; }

@media (max-width: 760px) {
  body { padding: 0; }
  .report { border-radius: 0; }
  .header, .section, .footer { padding: 24px 20px; }
  .header h1 { font-size: 24px; }
  .assembly-grid, .check-grid, .verdict-points { grid-template-columns: 1fr; }
  .section-no { font-size: 20px; }
}
"""

STAGE_CONFIG = {
    "宏观定调": {"number": "01", "cls": "macro", "code_cls": "code-blue", "avatar_cls": "avatar macro", "stage_cls": "stage-tag macro"},
    "中观筛选": {"number": "02", "cls": "meso",  "code_cls": "code-amber", "avatar_cls": "avatar meso",  "stage_cls": "stage-tag meso"},
    "微观决策": {"number": "03", "cls": "micro", "code_cls": "code-green", "avatar_cls": "avatar micro", "stage_cls": "stage-tag micro"},
}


def render_roundtable_html(data):
    """data 结构同 v1（见 docstring 兼容）：assembly / data_table / speeches / cross_check / verdict。"""
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
    <span class="header-brand">SKILL Palace · 圆桌会议报告</span>
  </div>
  <h1>{_html.escape(data['question'])}</h1>
  <div class="header-meta">
    <span class="meta-item">📅 {_html.escape(data.get('date',''))}</span>
    <span class="meta-item">📊 数据锚点：{_html.escape(data.get('source',''))}</span>
    <span class="meta-item">🤖 {_html.escape(data.get('assembly_method','assemble.py 确定性组阁'))}</span>
  </div>
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
  <div class="section-head"><span class="section-no">00</span><span class="section-title">动态组阁</span><span class="section-sub">命中 {a.get('tags_hit','?')} 标签 / {a.get('candidates','?')} 候选 → {a.get('formal_count','?')} 席位</span></div>
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
  <div class="section-head"><span class="section-no">01</span><span class="section-title">数据锚点</span><span class="section-sub">{_html.escape(data.get('date',''))} 行情快照</span></div>
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
  <div class="section-head"><span class="section-no">{cfg['number']}</span><span class="section-title">{stage_name}</span></div>
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
