# -*- coding: utf-8 -*-
"""圆桌会议报告 HTML 渲染器。

用法：
    from report.render import render_roundtable_html
    html = render_roundtable_html(data_dict)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

data_dict 结构见函数 render_roundtable_html 的 docstring。
"""

# ═══════ CSS 常量 ═══════
CSS = """\
:root {
  --bg: #FFFFFF;
  --surface: #F4F3F0;
  --border: #E0DED8;
  --text: #3A3936;
  --text-muted: #888780;
  --primary: #185FA5;
  --primary-light: #E6F1FB;
  --success: #639922;
  --success-light: #EAF3DE;
  --warning: #EF9F27;
  --warning-light: #FAEEDA;
  --danger: #E24B4A;
  --danger-light: #FCEBEB;
  --radius: 12px;
  --radius-sm: 8px;
  --font: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
  --font-mono: "SF Mono", "Cascadia Code", "Consolas", monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font); font-size: 14px; line-height: 1.65;
  color: var(--text); background: var(--surface); padding: 40px 16px;
}
.report { max-width: 900px; margin: 0 auto; background: var(--bg); border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
.header { background: var(--primary); color: #fff; padding: 36px 40px 28px; }
.header-label { font-size: 12px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.7; margin-bottom: 6px; }
.header h1 { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
.header-meta { display: flex; gap: 20px; font-size: 12px; opacity: 0.8; margin-top: 12px; flex-wrap: wrap; }
.section { padding: 28px 40px; border-bottom: 1px solid var(--border); }
.section:last-child { border-bottom: none; }
.section-title { font-size: 16px; font-weight: 600; color: var(--primary); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.section-title .badge { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; font-size: 13px; font-weight: 600; color: #fff; flex-shrink: 0; }
.badge-macro { background: var(--primary); } .badge-meso { background: var(--warning); } .badge-micro { background: var(--success); }
.assembly-cards { display: flex; gap: 16px; flex-wrap: wrap; }
.assembly-card { flex: 1 1 260px; background: var(--surface); border-radius: var(--radius); padding: 16px 20px; }
.assembly-card h4 { font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }
.assembly-card .expert-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.expert-tag { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; background: var(--bg); border: 1px solid var(--border); }
.expert-tag .code { font-family: var(--font-mono); font-size: 11px; font-weight: 600; padding: 1px 5px; border-radius: 4px; letter-spacing: 0.5px; }
.code-primary { background: var(--primary-light); color: var(--primary); } .code-warning { background: var(--warning-light); color: var(--warning); } .code-success { background: var(--success-light); color: var(--success); } .code-danger { background: var(--danger-light); color: var(--danger); }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 10px 12px; font-weight: 500; color: var(--text-muted); border-bottom: 2px solid var(--border); font-size: 12px; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
.data-table .up { color: #D85A30; } .data-table .down { color: var(--success); } .data-table .highlight { font-weight: 600; }
.speech-list { display: flex; flex-direction: column; gap: 16px; }
.speech-card { border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; }
.speech-head { display: flex; align-items: center; gap: 12px; padding: 14px 20px; border-bottom: 1px solid var(--border); }
.speech-head .avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: #fff; flex-shrink: 0; }
.avatar-macro { background: var(--primary); } .avatar-meso { background: var(--warning); } .avatar-micro { background: var(--success); }
.speech-head .info { flex: 1; } .speech-head .name { font-weight: 600; font-size: 14px; } .speech-head .role { font-size: 12px; color: var(--text-muted); margin-top: 1px; }
.speech-head .stage-tag { font-size: 11px; padding: 2px 10px; border-radius: 20px; font-weight: 500; }
.stage-macro { background: var(--primary-light); color: var(--primary); } .stage-meso { background: var(--warning-light); color: var(--warning); } .stage-micro { background: var(--success-light); color: var(--success); }
.speech-body { padding: 16px 20px; font-size: 14px; line-height: 1.75; color: var(--text); }
.speech-body blockquote { margin: 12px 0; padding: 10px 16px; border-left: 3px solid var(--primary); background: var(--primary-light); border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-weight: 500; }
.column-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.column-tag { display: inline-flex; align-items: center; gap: 3px; padding: 4px 12px; border-radius: 20px; font-size: 12px; background: var(--surface); border: 1px solid var(--border); }
.check-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.check-box { flex: 1 1 280px; border-radius: var(--radius); padding: 18px 20px; }
.check-box.consensus { background: var(--success-light); border: 1px solid #C0DD97; }
.check-box.divergence { background: var(--warning-light); border: 1px solid #FAC775; }
.check-box h4 { font-size: 13px; font-weight: 600; margin-bottom: 10px; }
.check-box ul { padding-left: 18px; } .check-box li { font-size: 13px; margin-bottom: 4px; line-height: 1.5; }
.verdict-box { background: linear-gradient(135deg, var(--success-light) 0%, #D4ECD0 100%); border: 2px solid var(--success); border-radius: var(--radius); padding: 24px 28px; }
.verdict-box h3 { font-size: 18px; font-weight: 600; color: #27500A; margin-bottom: 12px; }
.verdict-points { display: flex; flex-wrap: wrap; gap: 12px; }
.verdict-point { flex: 1 1 240px; background: rgba(255,255,255,0.7); border-radius: var(--radius-sm); padding: 14px 16px; font-size: 13px; line-height: 1.55; }
.verdict-point strong { display: block; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #3B6D11; margin-bottom: 4px; }
.footer { padding: 24px 40px; font-size: 12px; color: var(--text-muted); background: var(--surface); border-top: 1px solid var(--border); }
.footer p { margin-bottom: 4px; }
.mech-note { background: var(--surface); border-radius: var(--radius-sm); padding: 14px 18px; font-size: 12px; color: var(--text-muted); margin-top: 12px; }
.mech-note code { font-family: var(--font-mono); background: var(--bg); padding: 1px 6px; border-radius: 3px; font-size: 11px; }
@media (max-width: 640px) { .report { border-radius: 0; } .header, .section, .footer { padding: 20px 20px; } .assembly-cards { flex-direction: column; } .check-grid { flex-direction: column; } .header h1 { font-size: 20px; } }
"""

STAGE_CONFIG = {
    "宏观定调": {"number": 1, "class": "macro", "badge_class": "badge-macro", "avatar_class": "avatar-macro", "stage_class": "stage-macro", "code_class": "code-primary"},
    "中观筛选": {"number": 2, "class": "meso",  "badge_class": "badge-meso",  "avatar_class": "avatar-meso",  "stage_class": "stage-meso",  "code_class": "code-warning"},
    "微观决策": {"number": 3, "class": "micro", "badge_class": "badge-micro", "avatar_class": "avatar-micro", "stage_class": "stage-micro", "code_class": "code-success"},
}


def render_roundtable_html(data):
    """
    输入 data dict，返回完整 HTML 字符串。

    data 结构：
    {
        "question": "...",
        "date": "2026-08-05",
        "source": "westock 实时行情",
        "assembly": {
            "tags_hit": 25,
            "candidates": 15,
            "formal_count": 6,
            "column_count": 2,
            "stages": {  # keyed by "宏观定调"/"中观筛选"/"微观决策"
                "宏观定调": [{"code":"GS","name":"高善文"}, ...],
                "中观筛选": [...],
                "微观决策": [...]
            },
            "column": [{"code":"QG","name":"邱国鹭"}, ...],
            "mech_note_html": "可选机制说明 HTML"
        },
        "data_table": {
            "headers": ["标的","现价","当日","PE","YTD","60日","备注"],
            "rows": [  # 每行是一个 list，元素可以是 str 或 {"v":"...","class":"up/down/highlight/..."}
                ["上证指数","3,842",{"v":"+0.52%","class":"up"},"17.68",{"v":"-3.19%","class":"down"},{"v":"-8.83%","class":"down"},"20日 -3.24%"],
            ]
        },
        "speeches": [
            {
                "stage": "宏观定调",
                "code": "GS",
                "name": "高善文",
                "role": "中国宏观背景提供者",
                "is_decider": False,
                "content_html": "<p>段落</p><blockquote>关键句</blockquote>"
            },
        ],
        "cross_check": {"consensus": ["...","..."], "divergence": ["...","..."]},
        "verdict": {
            "title": "能上车——上\"价值车\"，不上\"行情车\"",
            "points": [{"label":"✅ 怎么上","text":"..."}, {"label":"❌ 怎么不上","text":"..."}, {"label":"🛡 纪律","text":"..."}],
            "oneline": "一句话总结"
        },
        "footer_note_html": "可选的页脚说明",
        "mech_note_html": "<strong>机制备注</strong>：... (详情)"
    }
    """
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>圆桌会议报告 · {data['question']}</title>
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
  <div class="header-label">SKILL Palace · 圆桌会议报告</div>
  <h1>{data['question']}</h1>
  <div class="header-meta">
    <span>📅 {data['date']}</span>
    <span>📊 数据锚点：{data['source']}</span>
    <span>🤖 组阁方式：assemble.py 确定性脚本</span>
    <span>📋 汇报人：SKILL Palace 圆桌会议</span>
  </div>
</div>"""


def _render_assembly(data):
    a = data["assembly"]
    stages_html = ""
    for stage_name, config in STAGE_CONFIG.items():
        experts = a["stages"].get(stage_name, [])
        if not experts:
            continue
        tags = "".join(
            f'<span class="expert-tag"><span class="code {config["code_class"]}">{e["code"]}</span>{e["name"]}</span>'
            for e in experts
        )
        stages_html += f"""\
    <div class="assembly-card">
      <h4><span class="badge {config['badge_class']}">{config['number']}</span> {stage_name}</h4>
      <div class="expert-tags">{tags}</div>
    </div>"""
    column_html = ""
    if a.get("column"):
        col_tags = "".join(
            f'<span class="column-tag"><span class="code code-success">{e["code"]}</span>{e["name"]}</span>'
            for e in a["column"]
        )
        column_html = f"""\
  <p style="font-size:12px;color:var(--text-muted);margin-top:10px;">
    列席备询：{col_tags}
  </p>"""
    mech = ""
    if a.get("mech_note_html"):
        mech = f'  <div class="mech-note">💡 {a["mech_note_html"]}</div>'
    return f"""\
<div class="section">
  <div class="section-title">🔧 动态组阁</div>
  <p style="font-size:13px;color:var(--text-muted);margin-bottom:14px;">
    问题解析 → 命中 <strong>{a.get('tags_hit','?')} 个标签</strong> → <strong>{a.get('candidates','?')} 位候选代码</strong> → 按三阶段收敛 → <strong>{a.get('formal_count','?')} 正式席位 + {a.get('column_count','?')} 列席备询</strong>
  </p>
  <div class="assembly-cards">
{stages_html}
  </div>
{column_html}
{mech}
</div>"""


def _render_data_table(data):
    dt = data.get("data_table", {})
    if not dt:
        return ""
    headers = dt.get("headers", [])
    rows = dt.get("rows", [])
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = ""
        for cell in row:
            if isinstance(cell, dict):
                cls = cell.get("class", "")
                tds += f'<td class="{cls}">{cell["v"]}</td>'
            else:
                tds += f"<td>{cell}</td>"
        trs += f"<tr>{tds}</tr>\n"
    return f"""\
<div class="section">
  <div class="section-title">📊 数据锚点（{data['date']} 快照）</div>
  <div style="overflow-x:auto;">
  <table class="data-table">
    <thead><tr>{th}</tr></thead>
    <tbody>{trs}</tbody>
  </table>
  </div>
</div>"""


def _render_speeches(data, stage_name):
    speeches = [s for s in data.get("speeches", []) if s.get("stage") == stage_name]
    if not speeches:
        return ""
    config = STAGE_CONFIG[stage_name]
    cards = ""
    for s in speeches:
        decider = " · 最终拍板" if s.get("is_decider") else ""
        cards += f"""\
    <div class="speech-card">
      <div class="speech-head">
        <div class="avatar {config['avatar_class']}">{s['code']}</div>
        <div class="info">
          <div class="name">{s['name']}</div>
          <div class="role">{s['role']}</div>
        </div>
        <span class="stage-tag {config['stage_class']}">{stage_name}{decider}</span>
      </div>
      <div class="speech-body">{s.get('content_html','')}</div>
    </div>
"""
    return f"""\
<div class="section">
  <div class="section-title">
    <span class="badge {config['badge_class']}">{config['number']}</span> {stage_name}
  </div>
  <div class="speech-list">
{cards}
  </div>
</div>"""


def _render_cross_check(data):
    cc = data.get("cross_check", {})
    if not cc:
        return ""
    con = "".join(f"<li>{i}</li>" for i in cc.get("consensus", []))
    div = "".join(f"<li>{i}</li>" for i in cc.get("divergence", []))
    return f"""\
<div class="section">
  <div class="section-title">🔍 交叉验证</div>
  <div class="check-grid">
    <div class="check-box consensus">
      <h4>✅ 共识</h4><ul>{con}</ul>
    </div>
    <div class="check-box divergence">
      <h4>⚡ 分歧</h4><ul>{div}</ul>
    </div>
  </div>
</div>"""


def _render_verdict(data):
    v = data.get("verdict", {})
    if not v:
        return ""
    pts = ""
    for p in v.get("points", []):
        pts += f'<div class="verdict-point"><strong>{p["label"]}</strong>{p["text"]}</div>'
    oneline = ""
    if v.get("oneline"):
        oneline = f'<p style="font-size:13px;color:var(--text-muted);margin-top:14px;text-align:center;"><strong>{v["oneline"]}</strong></p>'
    return f"""\
<div class="section">
  <div class="section-title">🏁 最终裁决</div>
  <div class="verdict-box">
    <h3>{v['title']}</h3>
    <div class="verdict-points">{pts}</div>
  </div>{oneline}
</div>"""


def _render_footer(data):
    note = data.get("footer_note_html", "")
    return f"""\
<div class="footer">
  <p><strong>⚠ 免责声明</strong>：{data.get('disclaimer','以上为圆桌框架推演，数据截至 ' + data['date'] + ' 快照，非投资建议。请以实时信息为准。')}</p>
  <p>{data.get('footer_html','本报告由 SKILL Palace 圆桌会议生成 · GitHub: kevin12369/skill-palace')}</p>
  {note}
</div>"""
