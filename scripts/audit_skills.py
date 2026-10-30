#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 SKILL_SPEC.md 对 skills/ 下全部 skill 做合规体检。

用法
----
    python scripts/audit_skills.py                # 人读报告（Markdown 表格）
    python scripts/audit_skills.py --json         # 机器读
    python scripts/audit_skills.py --skill charlie-munger   # 只看一个
    python scripts/audit_skills.py --severity ERROR         # 只看某一级别

退出码
------
    0  无 ERROR 级不合规（WARN / INFO 不影响结果，见文末「严重度口径」）
    1  存在 ERROR 级不合规
    2  前置条件缺失（找不到 skills/ 或 SKILL_SPEC.md）

严重度口径
----------
SKILL_SPEC.md 用 [必需] / [推荐] / 必须 / 推荐 区分条款强度，本脚本据此分三级：

    ERROR  SPEC 标为「必需」或「必须」的结构性条款被违反 → 阻断 CI
    WARN   推荐条款缺失，或 SPEC 有量化下限但全库未落地（如 §7「至少 3 个示例」）
    INFO   SPEC 未给明确阈值，只记录实际值供人工判断（如 SKILL.md 正文字数）

为什么要区分：P9 的约定是「体检发现的内容问题先出清单给人确认，不批量改 51 个目录」。
若把「示例不足 3 个」直接判成 ERROR，CI 立刻红，等于用 CI 逼一次未经确认的批量补写。
因此量化内容缺口一律 WARN，CI 只在结构被破坏时失败。

每条结果的条款出处见 CHECKS 表里的 `spec` 字段，可直接对回 SKILL_SPEC.md 的章节。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
INDEX_PATH = os.path.join(ROOT, "registry", "index.json")
SPEC_PATH = os.path.join(ROOT, "SKILL_SPEC.md")

REQUIRED_REFS = [
    "01-core-theories.md",
    "02-analysis-frameworks.md",
    "03-style-and-voice.md",
    "04-key-views-timeline.md",
    "05-publications.md",
    "06-glossary.md",
    "07-checklist.md",
    "08-style-anti-patterns.md",
]
REQUIRED_SECTIONS = ["目的", "何时使用", "核心思维模型", "工作流", "文风规范", "输出格式", "协作声明"]
PROFILE_SECTIONS = ["基本信息", "代表作与思想来源", "框架来源声明", "互补关系", "免责声明"]
PLACEHOLDERS = ["TODO", "TBD", "待补充", "FIXME", "<人物>", "<name>", "<topic>"]
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# id -> (严重度, SPEC 出处, 条款摘要)
CHECKS: dict[str, tuple[str, str, str]] = {
    "ST-01": ("ERROR", "§1 目录结构 / §9 配套文件", "SKILL.md 存在"),
    "ST-02": ("ERROR", "§1 / §6 PROFILE.md 规范", "PROFILE.md 存在"),
    "ST-03": ("ERROR", "§1 / §5 references 编号体系", "references/ 下 01–08 八个文件全齐"),
    "ST-04": ("ERROR", "§1 命名规则", "references/ 编号 01–08 连续、无多余编号文件"),
    "ST-05": ("WARN", "§1 [推荐] / §9 变体（推荐）", "SKILL-condensed.md 存在"),
    "ST-06": ("INFO", "§1 / §4 变体机制（~5KB）", "SKILL-condensed.md 体积"),
    "ST-07": ("WARN", "§8 治理文件（推荐）", "CITATION.cff 存在"),
    "ST-08": ("WARN", "§8 治理文件（推荐）", "CHANGELOG.md 存在"),
    "ST-09": ("ERROR", "§1 命名规则", "目录名为 kebab-case"),
    "ST-10": ("ERROR", "§1 命名规则 / §2", "目录名 == frontmatter name"),
    "ST-11": ("INFO", "§3 正文结构", "SKILL.md 正文字数（SPEC 未给下限）"),
    "FM-01": ("ERROR", "§2 frontmatter", "name / description / agent_created 三字段齐"),
    "FM-02": ("ERROR", "§2 / §9 frontmatter", "agent_created: true"),
    "FM-03": ("ERROR", "§2 description 要求 6", "description 含免责声明"),
    "FM-04": ("WARN", "§2 description 要求 5", "description 含互补声明"),
    "FM-05": ("INFO", "§2 description 要求 3/4", "description 含引号包裹的触发词 ≥3 处"),
    "FM-06": ("INFO", "§2 description 要求（整体）", "description 长度 ≥200 字符"),
    "BD-01": ("ERROR", "§3 正文结构 1", "H1 为「# <人物>思维框架与分析风格」"),
    "BD-02": ("ERROR", "§3 正文结构 2 / §9", "含「目的」区块"),
    "BD-03": ("ERROR", "§3 正文结构 3 / §9", "含「不声称代表」定位声明"),
    "BD-04": ("ERROR", "§3 正文结构 5 / §9", "核心思维模型 ≥5 个"),
    "BD-05": ("ERROR", "§3 正文结构 6 / §9", "工作流 ≥5 步"),
    "BD-06": ("ERROR", "§3 正文结构 7 / §9", "含「文风规范」区块"),
    "BD-07": ("ERROR", "§3 正文结构 8 / §9", "含「输出格式」区块"),
    "BD-08": ("ERROR", "§3 正文结构 9 / §9", "含「协作声明」区块"),
    "RF-01": ("WARN", "§5 / §9 01-core-theories", "01 至少 5 个理论块"),
    "RF-02": ("WARN", "§5 / §9 08-style-anti-patterns", "08 至少 4 个反例"),
    "RF-03": ("ERROR", "§5 / §9 07-checklist", "07 覆盖 内容 / 风格 / 合规 三维度"),
    "RF-04": ("ERROR", "§9 质量检查 正反双校验", "07 含勾选项（- [ ]）、08 每例含三段结构"),
    "RF-05": ("INFO", "§5 references 内容要求", "单个 references 文件 ≥500 字节"),
    "EX-00": ("ERROR", "§7 examples 规范 / §9", "examples/INDEX.md 存在"),
    "EX-01": ("ERROR", "§7 / §9", "INDEX.md 内的 .md 链接全部指向真实文件"),
    "EX-02": ("WARN", "§7 / §9 至少 3 个示例", "examples/ 示例正文 ≥3 个"),
    "EX-03": ("WARN", "§1 命名规则", "examples 文件名带两位数字前缀"),
    "EX-04": ("WARN", "§7", "示例含「输入」与「校准说明」"),
    "EX-05": ("ERROR", "§7 / §9 质量检查", "示例正文结尾含「AI 生成声明」"),
    "PF-01": ("ERROR", "§6 PROFILE.md 规范 / §9", "PROFILE.md 五个必需区块齐全"),
    "CT-01": ("WARN", "§8 / §9 配套文件", "CITATION.cff 含 cff-version/title/authors/version/date-released"),
    "CL-01": ("WARN", "§8 / §9", "CHANGELOG.md 含已发布版本条目"),
    "CL-02": ("WARN", "§9", "CHANGELOG 版本号语义化格式"),
    "QL-01": ("ERROR", "§9 质量检查", "无 TODO / TBD / 占位符"),
    "QL-02": ("ERROR", "§9 质量检查 / §5 正反双校验", "07 与 08 同时存在（双校验完整）"),
    "QL-03": ("WARN", "§9 质量检查 互补关系", "协作声明与 registry/index.json 的 complements 一致"),
    "QL-04": ("ERROR", "§9 质量检查 已故人物", "按 registry 的 living 字段核对致敬 / 伦理声明"),
    "QL-05": ("INFO", "§6 PROFILE 基本信息", "生卒与现任职务是否给了事实依据"),
}

rows: list[dict] = []


def add(skill: str, cid: str, actual: str, expected: str) -> None:
    sev, spec, clause = CHECKS[cid]
    rows.append({"skill": skill, "id": cid, "severity": sev, "spec": spec,
                 "clause": clause, "actual": actual, "expected": expected})


def read(path: str) -> str:
    """读文本并统一换行为 LF（Windows 工作区里 build.py 写出的文件是 CRLF）。"""
    with open(path, "rb") as f:
        return f.read().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def section_body(text: str, keyword: str) -> str:
    """取 `## <keyword>` 到下一个 `## ` 之间的正文。"""
    m = re.search(r"^## [^\n]*" + re.escape(keyword) + r"[^\n]*\n(.*?)(?=^## |\Z)",
                  text, re.M | re.S)
    return m.group(1) if m else ""


def frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return (m.group(1), text[m.end():]) if m else ("", text)


def audit_one(slug: str, base: str, index_by_name: dict) -> None:
    skill_md = os.path.join(base, "SKILL.md")

    # ---------- ST 结构 ----------
    if not os.path.isfile(skill_md):
        add(slug, "ST-01", "缺失", "skills/<name>/SKILL.md 存在")
        return
    text = read(skill_md)
    fm, body = frontmatter(text)

    if not KEBAB_RE.match(slug):
        add(slug, "ST-09", slug, "kebab-case（小写字母/数字/单连字符）")

    profile = os.path.join(base, "PROFILE.md")
    if not os.path.isfile(profile):
        add(slug, "ST-02", "缺失", "PROFILE.md 存在")
        profile_text = ""
    else:
        profile_text = read(profile)

    refs_dir = os.path.join(base, "references")
    present_refs = sorted(os.listdir(refs_dir)) if os.path.isdir(refs_dir) else []
    missing_refs = [r for r in REQUIRED_REFS if r not in present_refs]
    if missing_refs:
        add(slug, "ST-03", "缺 " + ", ".join(missing_refs), "01–08 八个文件全齐")
    extra = [r for r in present_refs
             if r.endswith(".md") and r not in REQUIRED_REFS and re.match(r"^\d\d-", r)]
    if extra:
        add(slug, "ST-04", "多余编号文件 " + ", ".join(extra), "编号仅 01–08")

    condensed = os.path.join(base, "SKILL-condensed.md")
    if not os.path.isfile(condensed):
        add(slug, "ST-05", "缺失", "SKILL-condensed.md 存在")
    else:
        size = len(read(condensed).encode("utf-8"))
        if size < 1024:
            add(slug, "ST-06", f"{size} B", "非空壳（≥1024 B；SPEC 原文写 ~5KB）")
        else:
            rows.append({"skill": slug, "id": "ST-06", "severity": "INFO",
                         "spec": CHECKS["ST-06"][1], "clause": CHECKS["ST-06"][2],
                         "actual": f"{size} B", "expected": "SPEC 原文 ~5KB（实际全库 1.8–3.0 KB）"})

    citation = os.path.join(base, "CITATION.cff")
    if not os.path.isfile(citation):
        add(slug, "ST-07", "缺失", "CITATION.cff 存在")
    changelog = os.path.join(base, "CHANGELOG.md")
    if not os.path.isfile(changelog):
        add(slug, "ST-08", "缺失", "CHANGELOG.md 存在")

    body_chars = len(body.strip())
    rows.append({"skill": slug, "id": "ST-11", "severity": "INFO",
                 "spec": CHECKS["ST-11"][1], "clause": CHECKS["ST-11"][2],
                 "actual": f"{body_chars} 字符", "expected": "SPEC 未规定下限（建议补 ≥3000）"})

    # ---------- FM frontmatter ----------
    keys = [l.split(":", 1)[0] for l in fm.split("\n") if l and not l.startswith((" ", "\t"))]
    for need in ("name", "description", "agent_created"):
        if need not in keys:
            add(slug, "FM-01", "缺 " + need, "name / description / agent_created 三字段")
    if "agent_created" in keys and not re.search(r"^agent_created:\s*true\s*$", fm, re.M):
        add(slug, "FM-02", re.search(r"^agent_created:.*$", fm, re.M).group(0).strip(),
            "agent_created: true")

    fm_name = None
    m = re.search(r"^name:\s*(.+)$", fm, re.M)
    if m:
        fm_name = m.group(1).strip().strip('"').strip("'")
        if fm_name != slug:
            add(slug, "ST-10", f"name: {fm_name}", f"与目录名 {slug} 一致")

    m = re.search(r"^description:\s*[\"']?(.*?)[\"']?\s*$", fm, re.M)
    desc = m.group(1) if m else ""
    if not re.search(r"不声称|不代表|不冒充", desc):
        add(slug, "FM-03", "description 未见免责措辞", "含「不声称代表本人」类声明")
    if "互补" not in desc:
        add(slug, "FM-04", "description 未见「互补」", "声明与其他 skill 的互补关系")
    quoted = len(re.findall(r'[“"「][^”"」]{2,}[”"」]', desc))
    if quoted < 3:
        add(slug, "FM-05", f"引号触发词 {quoted} 处", "≥3 处（关键词清单 / 问题示例）")
    if len(desc) < 200:
        add(slug, "FM-06", f"{len(desc)} 字符", "≥200 字符（承载 6 要素）")

    # ---------- BD 正文 ----------
    h1 = body.strip().split("\n", 1)[0] if body.strip() else ""
    if not re.match(r"^# .+思维框架与分析风格\s*$", h1):
        add(slug, "BD-01", h1 or "（无 H1）", "# <人物>思维框架与分析风格")
    headings = [l[3:].strip() for l in text.split("\n") if l.startswith("## ")]
    for cid, kw in (("BD-02", "目的"), ("BD-06", "文风规范"),
                    ("BD-07", "输出格式"), ("BD-08", "协作声明")):
        if not any(kw in h for h in headings):
            add(slug, cid, f"二级标题未见「{kw}」", f"含「{kw}」区块")
    if "不声称代表" not in text:
        add(slug, "BD-03", "全文未见「不声称代表」", "显式定位声明")

    model_sec = section_body(text, "核心思维模型")
    n_models = len(re.findall(r"^-\s+", model_sec, re.M)) or len(re.findall(r"^\d+\.\s", model_sec, re.M))
    if n_models < 5:
        add(slug, "BD-04", f"{n_models} 个", "≥5 个核心思维模型")
    flow_sec = section_body(text, "工作流")
    n_steps = len(re.findall(r"^\d+\.\s", flow_sec, re.M))
    if n_steps < 5:
        add(slug, "BD-05", f"{n_steps} 步", "≥5 步工作流")

    # ---------- RF references ----------
    if os.path.isdir(refs_dir):
        p01 = os.path.join(refs_dir, "01-core-theories.md")
        if os.path.isfile(p01):
            n_theories = len(re.findall(r"^## 理论\s*\d+", read(p01), re.M))
            if n_theories < 5:
                add(slug, "RF-01", f"{n_theories} 个理论块（## 理论 N）", "≥5 个")
        p08 = os.path.join(refs_dir, "08-style-anti-patterns.md")
        p07 = os.path.join(refs_dir, "07-checklist.md")
        if os.path.isfile(p08):
            t08 = read(p08)
            n_anti = len(re.findall(r"^## 反例", t08, re.M))
            if n_anti < 4:
                add(slug, "RF-02", f"{n_anti} 个反例（## 反例 N）", "≥4 个")
            thirds = sum(1 for seg in re.split(r"^## 反例", t08, flags=re.M)[1:]
                         if "错误输出" in seg and "正确改写" in seg)
            if n_anti and thirds < n_anti:
                add(slug, "RF-04", f"{thirds}/{n_anti} 个反例含「错误输出+原因+正确改写」", "每例三段齐全")
        else:
            add(slug, "QL-02", "08-style-anti-patterns.md 缺失", "07+08 双校验完整")
        if os.path.isfile(p07):
            t07 = read(p07)
            lacking = [d for d in ("内容", "风格", "合规") if d not in t07]
            if lacking:
                add(slug, "RF-03", "缺维度 " + "/".join(lacking), "内容 / 风格 / 合规 三维度")
            if "- [ ]" not in t07 and "- [x]" not in t07.lower():
                add(slug, "RF-04", "07 无勾选项", "含 `- [ ]` 形式的 checklist 项")
        else:
            add(slug, "QL-02", "07-checklist.md 缺失", "07+08 双校验完整")

        for ref in present_refs:
            if not ref.endswith(".md"):
                continue
            sz = len(read(os.path.join(refs_dir, ref)).encode("utf-8"))
            if sz < 500:
                add(slug, "RF-05", f"{ref} 仅 {sz} B", "≥500 B")

    # ---------- EX examples ----------
    ex_dir = os.path.join(base, "examples")
    if not os.path.isdir(ex_dir):
        add(slug, "EX-00", "无 examples/ 目录", "examples/INDEX.md 存在")
    else:
        idx_path = os.path.join(ex_dir, "INDEX.md")
        if not os.path.isfile(idx_path):
            add(slug, "EX-00", "缺失 INDEX.md", "examples/INDEX.md 存在")
        else:
            idx_text = read(idx_path)
            phantoms = []
            for tgt in re.findall(r"\]\(([^)#]+\.md)\)", idx_text):
                if not os.path.isfile(os.path.join(ex_dir, tgt)):
                    phantoms.append(tgt)
            if phantoms:
                add(slug, "EX-01", "幻影链接 " + ", ".join(sorted(set(phantoms))),
                    "INDEX 内每个 .md 链接都指向真实文件")
        examples = [f for f in sorted(os.listdir(ex_dir)) if f.endswith(".md") and f != "INDEX.md"]
        if len(examples) < 3:
            add(slug, "EX-02", f"{len(examples)} 个示例正文", "≥3 个（框架应用 + 风格校准 + 专项场景）")
        no_prefix = [f for f in examples if not re.match(r"^\d\d-", f) and not re.match(r"^example-\d\d", f)]
        if no_prefix:
            add(slug, "EX-03", "无数字前缀 " + ", ".join(no_prefix), "两位数字前缀")
        for f in examples:
            t = read(os.path.join(ex_dir, f))
            lacking = [k for k in ("输入", "校准说明") if k not in t]
            if lacking:
                add(slug, "EX-04", f"{f} 缺 " + "/".join(lacking), "含「输入」与「校准说明」")
            # EX-05：示例正文是最像「真人观点 / 真实研报」的形态，必须自带 AI 生成声明。
            # 只认文末 20 行内的声明，避免正文里顺嘴提一句「AI」也算数。
            tail = "\n".join(t.rstrip().split("\n")[-20:])
            if "AI 生成声明" not in tail:
                add(slug, "EX-05", f"{f} 文末无 AI 生成声明", "文末 20 行内出现「AI 生成声明」")

    # ---------- PF PROFILE ----------
    if profile_text:
        ph = [l[3:].strip() for l in profile_text.split("\n") if l.startswith("## ")]
        lacking = [s for s in PROFILE_SECTIONS if not any(s in h for h in ph)]
        if lacking:
            add(slug, "PF-01", "缺区块 " + "/".join(lacking), "基本信息/代表作与思想来源/框架来源声明/互补关系/免责声明")

    # ---------- CT CITATION ----------
    if os.path.isfile(citation):
        ct = read(citation)
        lacking = [k for k in ("cff-version:", "title:", "authors:", "version:", "date-released:")
                   if k not in ct]
        if lacking:
            add(slug, "CT-01", "缺 " + ", ".join(lacking), "CFF 必填五项")

    # ---------- CL CHANGELOG ----------
    if os.path.isfile(changelog):
        cl = read(changelog)
        versions = re.findall(r"^##\s*\[?v?(\d+\.\d+\.\d+)\]?", cl, re.M)
        if not versions:
            add(slug, "CL-01", "未见 `## [x.y.z]` 条目", "至少一条已发布版本条目")
        else:
            bad = [v for v in versions if not SEMVER_RE.match(v)]
            if bad:
                add(slug, "CL-02", "非语义化版本 " + ", ".join(bad), "X.Y.Z")

    # ---------- QL 质量 ----------
    hits = [p for p in PLACEHOLDERS if p in text]
    if hits:
        add(slug, "QL-01", "命中 " + ", ".join(hits), "无占位符 / TODO")
    entry = index_by_name.get(slug)
    if entry:
        collab = section_body(text, "协作声明")
        lacking = []
        for c in entry.get("complements", []):
            person = (index_by_name.get(c) or {}).get("person", "")
            if c not in collab and (not person or person not in collab):
                lacking.append(c)
        if lacking:
            add(slug, "QL-03", "协作声明未提及 " + ", ".join(lacking),
                "逐条对应 registry/index.json 的 complements")
    # QL-04：已故人物的致敬 / 伦理声明。名单来源是 registry/index.json 的 living 字段
    # （由 build.py 从 tools/skill-gen/people.py 生成），不再靠人工确认或关键词猜测。
    #   living === False → 必须出现「人物状态」且写明「逝世」
    #   living === True  → 必须出现「人物状态」且写明「在世」
    #   living === None  → 必须出现「条目性质」（方法论条目）或「待考」（生卒未定）
    living = entry.get("living") if entry else "无 registry 条目"
    merged = text + "\n" + profile_text
    if living is False:
        want = ("人物状态", "逝世")
    elif living is True:
        want = ("人物状态", "在世")
    elif living is None:
        want = None
    else:
        want = None
    if want:
        miss = [k for k in want if k not in merged]
        if miss:
            add(slug, "QL-04", "living=" + str(living) + " 但缺少 " + " / ".join(miss),
                "按 living 字段渲染人物状态声明")
    elif living is None and entry:
        if "条目性质" not in merged and "待考" not in merged:
            add(slug, "QL-04", "living=None 但既无「条目性质」也无「待考」说明",
                "方法论条目写「条目性质」，生卒未定写「待考」")
    rows.append({"skill": slug, "id": "QL-04", "severity": "INFO",
                 "spec": CHECKS["QL-04"][1], "clause": CHECKS["QL-04"][2],
                 "actual": "living=" + str(living),
                 "expected": "已故写明逝世并致意／在世声明不代表当前观点／方法论标注条目性质"})
    # QL-05：生卒与现任职务的事实依据。只统计覆盖率，不判合规——没查证过的条目
    # 宁可留空也不该编一个出处，所以「无」本身不算错，只说明这块还是欠债。
    n_src = len((entry or {}).get("sources") or [])
    rows.append({"skill": slug, "id": "QL-05", "severity": "INFO",
                 "spec": CHECKS["QL-05"][1], "clause": CHECKS["QL-05"][2],
                 "actual": ("有 %d 条事实依据" % n_src) if n_src else "无事实依据",
                 "expected": "已故人物与有任职变动的在世人物应给出可查证出处"})


CLARIFICATIONS = [
    ("§1 / §4 「精简版 ~5KB」",
     "SPEC 写 `~5KB`，仓库实测 1.8–3.0 KB（最小 hong-hao 1811 B，最大 william-oneil 3022 B）。"
     "「~5KB」既可理解为上限也可理解为目标值，两种读法结论相反。",
     "建议改为「1.5–3.5 KB，上限不超过完整版的 40%」——现在的事实区间本身就是合格证据。"),
    ("§3 正文结构「定位声明（必须）」",
     "SPEC §3 把「定位声明」列为第 3 个独立区块并要求按顺序出现，但 51 个 skill 里没有任何一个"
     "有独立的 `## 定位声明` 小节——声明一律内嵌在「目的」段末或开头的引用块里。",
     "两种收敛方式选其一：① 改 SPEC，写「定位声明可内嵌，但必须出现『不声称代表』原句」；"
     "② 补 51 个小节。建议 ①。"),
    ("§3 正文结构 8 「输出模板」",
     "SPEC 称为「输出模板」，实际 51 个 skill 一律用 `## 输出格式`。规范名与文件实际标题不一致。",
     "建议 SPEC 改为「输出格式（输出模板）」，或脚本按同义词匹配——本脚本已按「输出格式」匹配。"),
    ("§7 「至少 3 个示例」",
     "原始状态：5 个 skill 有 3 篇手写示例、46 个 skill 为 0（INDEX 里只有规划选题，共 102 条幻影引用）。"
     "真要按 SPEC 补齐约需 138 篇，一度被认为是「内容生产而非格式修复」。",
     "已落地：`build.py` 的 write_missing_examples() 按「补到 3 篇为止」生成框架演练"
     "（选题取自 examples_index，步骤取自 theories，反例篇取自 anti_patterns，"
     "只补缺失、覆盖前先数已有篇数，手写的 15 篇不动），全库 51×3=153 篇。"
     "EX-02 已升为可回归项，不再是挂账。"),
    ("§5 / §9 「01-core-theories.md 至少 5 个理论」",
     "条款是明文下限，但原始状态有 15 个 skill 的 01 文件只有 1–4 个理论块（kondratiev 只有 1 个）。"
     "这是全库最早一批迁移时的欠债，不是格式问题——补齐需要写内容，不能靠脚本改格式。",
     "已落地：按各条目 `frameworks` 里已声明、但 01 文件没展开的条目补写 39 个理论块，"
     "theories 分布现为 {5: 16, 6: 35}，无一 <5。RF-01 现在可以直接当回归检查用。"),
    ("§5 / §9 「SKILL.md 最小长度」",
     "SPEC 全文没有任何正文字数下限，只在 §9 列了「模型 ≥5 / 工作流 ≥5 步」等结构性下限。"
     "结果是「结构齐全但内容很薄」也能过审。",
     "建议补一条量化下限，例如「SKILL.md 正文 ≥3000 字符，references 单文件 ≥1500 字符」，"
     "并允许按人物资料丰沛度上下浮动 20%。"),
    ("§9「互补关系与 registry/index.json 一致」",
     "条款要求「一致」但没说清是逐条列举还是允许概括。原始状态：49/51 的「协作声明」是模板化措辞"
     "（「涉及互补领域 → 优先用 `warren-buffett` 等」），读者看不出到底能找谁。",
     "已落地：按更严的读法（必须逐条点名）执行——`build.py` 的 collab_block() 遍历 complements，"
     "逐个渲染成「与 `<slug>`（中文名）互补：<对方领域> 方向的问题优先用它」，51/51 全部点名。"
     "建议 SPEC 把这句读法写死，免得以后又退回概括。"),
    ("§9「如人物已故，含致敬与伦理声明」",
     "「已故」需要一份权威名单，SPEC 没有提供。原始脚本只能靠「致敬/纪念/伦理」关键词猜，"
     "既会漏判（生前表述里也可能出现这些词）也会误判（漏写声明的人反而因别处出现关键词而通过）。",
     "已落地：`tools/skill-gen/people.py` 增加 `living` / `died` 字段 → `build.py` 写入 "
     "`registry/index.json` 并按在世 / 已故 / 方法论三态渲染「人物状态」「条目性质」声明。"
     "QL-04 因此升级为 ERROR，直接按 registry 的 `living` 核对，不再依赖关键词。"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="按 SKILL_SPEC.md 体检全部 skill")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    ap.add_argument("--skill", help="只体检指定 skill（目录名）")
    ap.add_argument("--severity", choices=["ERROR", "WARN", "INFO"], help="只看某一严重度")
    args = ap.parse_args()

    if not os.path.isdir(SKILLS_DIR):
        print(f"[FATAL] 找不到 skills/：{SKILLS_DIR}")
        return 2
    if not os.path.isfile(SPEC_PATH):
        print(f"[FATAL] 找不到 SKILL_SPEC.md：{SPEC_PATH}")
        return 2

    index_by_name = {}
    if os.path.isfile(INDEX_PATH):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            index_by_name = {s["name"]: s for s in json.load(f).get("skills", [])}

    slugs = sorted(d for d in os.listdir(SKILLS_DIR)
                   if not d.startswith("_") and os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
    if args.skill:
        slugs = [s for s in slugs if s == args.skill]
        if not slugs:
            print(f"[FATAL] 没有这个 skill：{args.skill}")
            return 2

    for slug in slugs:
        audit_one(slug, os.path.join(SKILLS_DIR, slug), index_by_name)

    rows.sort(key=lambda r: (r["skill"], r["id"]))
    if args.severity:
        shown = [r for r in rows if r["severity"] == args.severity]
    else:
        shown = rows

    err = [r for r in rows if r["severity"] == "ERROR"]
    warn = [r for r in rows if r["severity"] == "WARN"]
    info = [r for r in rows if r["severity"] == "INFO"]

    by_skill_bad: dict[str, set[str]] = defaultdict(set)
    for r in err + warn:
        by_skill_bad[r["skill"]].add(r["id"])
    clean = [s for s in slugs if s not in by_skill_bad]
    # 历史欠债 / 口径待澄清条款：SPEC 有明文下限但全库未落地，或条款措辞有两种合理解读。
    # 剔除这三条后的「结构合规数」更能反映仓库的真实状态。
    # 仍未落地的欠债条款：SPEC 有明文下限、但全库还没做到，单独统计而不是混进「不合规」，
    # 否则真正的结构性问题会被数量淹没。哪一条补齐了就从这里删掉，报告里的口径自动跟着变。
    DEBT_NOTES: dict[str, str] = {}
    DEBT = set(DEBT_NOTES)
    bad_strict: dict[str, set[str]] = defaultdict(set)
    for r in err + warn:
        if r["id"] not in DEBT:
            bad_strict[r["skill"]].add(r["id"])
    clean_strict = [s for s in slugs if s not in bad_strict]
    clause_count = Counter(r["id"] for r in err + warn)

    if args.json:
        print(json.dumps({
            "ok": not err,
            "skills_audited": len(slugs),
            "clean_skills": len(clean),
            "clean_skills_excluding_debt": len(clean_strict),
            "counts": {"error": len(err), "warn": len(warn), "info": len(info)},
            "issued_skills": {s: sorted(v) for s, v in sorted(by_skill_bad.items())},
            "rows": shown,
            "clarifications": [{"item": a, "problem": b, "suggestion": c}
                              for a, b, c in CLARIFICATIONS],
        }, ensure_ascii=False, indent=2))
        return 0 if not err else 1

    print("=" * 100)
    print("SKILL_SPEC 全量合规体检")
    print("=" * 100)
    print(f"体检对象：{len(slugs)} 个 skill（skills/_template 不计入）")
    print(f"结果：ERROR {len(err)} 条 ／ WARN {len(warn)} 条 ／ INFO {len(info)} 条")
    print(f"完全合规（无 ERROR 也无 WARN）：{len(clean)} 个 → {', '.join(clean) if clean else '（无）'}")
    if DEBT_NOTES:
        label = " / ".join(f"{k} {v}" for k, v in DEBT_NOTES.items())
        print(f"剔除「历史欠债」{len(DEBT_NOTES)} 条（{label}）后："
              f"{len(clean_strict)}/{len(slugs)} 个 skill 结构完全合规")
    else:
        print(f"无历史欠债项：{len(clean_strict)}/{len(slugs)} 个 skill 结构完全合规")
    print()

    print("-" * 100)
    print("| skill | 条款 | 严重度 | 不合规项 | 实际值 | 期望值 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for r in shown:
        if r["severity"] == "INFO" and not args.severity:
            continue  # INFO 逐条太长，改在下方「量化分布」里汇总
        print(f"| {r['skill']} | {r['id']} {r['spec']} | {r['severity']} | {r['clause']} | "
              f"{r['actual']} | {r['expected']} |")
    print("-" * 100)
    print()

    print("【问题分布】按条款统计（ERROR + WARN）")
    for cid, n in sorted(clause_count.items(), key=lambda x: (-x[1], x[0])):
        sev, spec, clause = CHECKS[cid]
        print(f"  {cid:6} {n:3} 次  [{sev}] {spec} — {clause}")
    if not clause_count:
        print("  （无）")
    print()

    print("【量化分布】INFO 项汇总")
    for cid in ("ST-06", "ST-11", "QL-04", "QL-05"):
        vals = [r for r in rows if r["id"] == cid]
        if cid == "QL-04":
            # 只统计「通过」的实例行（actual 恰为 living=True/False/None）；
            # 不合规行已在上面按条列出，不重复计入分档。
            vals_ok = [r for r in vals
                       if re.fullmatch(r"living=(True|False|None)", r["actual"])]
            dist: dict[str, int] = {}
            for r in vals_ok:
                key = r["actual"].replace("living=", "")
                dist[key] = dist.get(key, 0) + 1
            pretty = " / ".join(f"{k} {v}" for k, v in sorted(dist.items())) or "（无）"
            print(f"  QL-04 按 registry 的 living 分档：{pretty}")
        elif cid == "ST-06":
            nums = sorted(int(r["actual"].split()[0]) for r in vals)
            if nums:
                print(f"  ST-06 SKILL-condensed.md 体积：{nums[0]}–{nums[-1]} B（中位 {nums[len(nums)//2]} B），共 {len(nums)} 份")
        elif cid == "ST-11":
            nums = sorted(int(r["actual"].split()[0]) for r in vals)
            if nums:
                print(f"  ST-11 SKILL.md 正文字数：{nums[0]}–{nums[-1]} 字符（中位 {nums[len(nums)//2]}）")
        elif cid == "QL-05":
            have = {r["skill"] for r in vals if r["actual"].startswith("有")}
            dead = {r["skill"] for r in rows
                    if r["id"] == "QL-04" and r["actual"] == "living=False"}
            print(f"  QL-05 带事实依据的条目：{len(have)}/{len(vals)}"
                  f"（其中已故 {len(have & dead)}/{len(dead)}）")
    print()

    print("=" * 100)
    print("规范本身需要澄清的点（SKILL_SPEC.md 与实际做法的落差）")
    print("=" * 100)
    for i, (item, problem, suggestion) in enumerate(CLARIFICATIONS, 1):
        print(f"{i}. {item}")
        print(f"   问题：{problem}")
        print(f"   建议：{suggestion}")
    print()
    if err:
        print("结论：存在 ERROR 级不合规，见上表 ❌")
    elif warn:
        print("结论：无结构性不合规 ✅（WARN 项为内容缺口，建议按上面清单人工确认后分批处理）")
    else:
        print("结论：全部通过 ✅（ERROR 0 ／ WARN 0，INFO 项为量化记录）")
    return 0 if not err else 1


if __name__ == "__main__":
    sys.exit(main())
