#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""registry 漂移校验：比对 registry/ 两份索引、skills/ 文件系统、SKILL.md frontmatter。

用途
----
`tools/skill-gen/build.py` 会重写 registry/index.json 与 registry/roundtable-matrix.json。
一旦有人手改索引、或改完 people.py 忘了重跑构建，索引与真实目录就会漂移。
本脚本把这种漂移变成可重复运行的检查：

    python scripts/check_registry.py          # 人读报告
    python scripts/check_registry.py --json   # 机器读

退出码
------
    0  全部一致（可能有 WARN / INFO，但无 ERROR）
    1  存在 ERROR（漂移）
    2  前置条件不成立（找不到 skills/ 或索引文件、JSON 解析失败）

输出约定
--------
每条差异都指到「哪一个 skill 的哪一个字段」，不输出笼统的"不一致"。
格式：`[ERROR] <检查号> <skill 或对象> :: <字段> :: <说明>`
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
MATRIX_PATH = os.path.join(ROOT, "registry", "roundtable-matrix.json")

# index.json 每条 skill 必须具备的字段（缺一即 ERROR）
REQUIRED_FIELDS = [
    "name", "person", "domain", "domain_cn", "region", "status",
    "frameworks", "style_keywords", "roundtable_role", "roundtable_tags",
    "complements", "path", "code",
]
# 这些字段必须是「非空字符串数组」
NONEMPTY_LIST_FIELDS = ["frameworks", "style_keywords", "roundtable_tags"]
LIST_FIELDS = ["frameworks", "style_keywords", "roundtable_tags", "complements"]
STR_FIELDS = ["name", "person", "domain", "domain_cn", "region", "status",
              "roundtable_role", "path", "code"]
VALID_STATUS = {"released"}
VALID_STAGES = {"宏观定调", "中观筛选", "微观决策"}
CODE_RE = re.compile(r"^[A-Z]{2,3}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

problems: list[tuple[str, str, str, str]] = []  # (level, check, subject, message)


def add(level: str, check: str, subject: str, message: str) -> None:
    problems.append((level, check, subject, message))


def load_json(path: str, label: str) -> dict:
    if not os.path.isfile(path):
        print(f"[FATAL] 找不到 {label}：{os.path.relpath(path, ROOT)}")
        sys.exit(2)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FATAL] {label} 不是合法 JSON：{e}")
        add("ERROR", "R01", label, f"JSON 解析失败：{e}")
        return {}


def real_skill_dirs() -> tuple[list[str], list[str]]:
    """返回 (真实 skill 目录名, 被忽略的非 skill 目录名)。

    判定标准：`skills/<name>/` 是一级目录、不以 `_` 开头、且**含有 SKILL.md**。
    这样本地残留的空壳目录（如被 .gitignore 屏蔽的 skills/skills/）不会被误判成漂移。
    """
    if not os.path.isdir(SKILLS_DIR):
        print(f"[FATAL] 找不到 skills/ 目录：{SKILLS_DIR}")
        sys.exit(2)
    ok, ignored = [], []
    for name in sorted(os.listdir(SKILLS_DIR)):
        path = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(path) or name.startswith("_"):
            continue
        (ok if os.path.isfile(os.path.join(path, "SKILL.md")) else ignored).append(name)
    return ok, ignored


def frontmatter_name(skill_md: str) -> str | None:
    if not os.path.isfile(skill_md):
        return None
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    nm = re.search(r"^name:\s*(.+)$", m.group(1), re.MULTILINE)
    return nm.group(1).strip() if nm else None


def changelog_top_version(slug: str) -> str | None:
    """取 skill CHANGELOG.md 中最高的已发布版本号（跳过 Unreleased）。"""
    path = os.path.join(SKILLS_DIR, slug, "CHANGELOG.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    versions = re.findall(r"^##\s*\[?v?(\d+\.\d+\.\d+)\]?", text, re.MULTILINE)
    if not versions:
        return None
    key = lambda v: tuple(int(x) for x in v.split("."))
    return max(versions, key=key)


def main() -> int:
    ap = argparse.ArgumentParser(description="校验 registry 索引与 skills/ 目录、相互字段是否一致")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = ap.parse_args()

    index = load_json(INDEX_PATH, "registry/index.json")
    matrix = load_json(MATRIX_PATH, "registry/roundtable-matrix.json")
    dirs, ignored_dirs = real_skill_dirs()

    entries = index.get("skills", [])
    if not isinstance(entries, list) or not entries:
        add("ERROR", "R01", "registry/index.json", "缺少 skills 数组或为空")

    by_name: dict[str, dict] = {}
    for i, e in enumerate(entries):
        nm = e.get("name") if isinstance(e, dict) else None
        if not isinstance(e, dict) or not nm:
            add("ERROR", "R03", f"index.skills[{i}]", "条目缺少 name 字段")
            continue
        if nm in by_name:
            add("ERROR", "R08", nm, "index.skills 中 name 重复出现")
        by_name[nm] = e

    # ---------- R03 字段完整性 ----------
    for nm, e in by_name.items():
        for field in REQUIRED_FIELDS:
            if field not in e:
                add("ERROR", "R03", nm, f"字段缺失：{field}")
        for field in STR_FIELDS:
            if field in e and not (isinstance(e[field], str) and e[field].strip()):
                add("ERROR", "R03", nm, f"字段 {field} 必须是非空字符串，实际 {e[field]!r}")
        for field in NONEMPTY_LIST_FIELDS:
            if field in e and not (isinstance(e[field], list) and e[field]):
                add("ERROR", "R03", nm, f"字段 {field} 必须是非空数组，实际 {e[field]!r}")
        for field in LIST_FIELDS:
            v = e.get(field)
            if v is None:
                continue
            if not isinstance(v, list):
                add("ERROR", "R03", nm, f"字段 {field} 必须是数组，实际 {type(v).__name__}")
            elif any(not isinstance(x, str) or not x.strip() for x in v):
                add("ERROR", "R03", nm, f"字段 {field} 含空值或非字符串元素：{v!r}")
            elif len(set(v)) != len(v):
                dup = [x for x, n in Counter(v).items() if n > 1]
                add("ERROR", "R03", nm, f"字段 {field} 含重复项：{dup}")

    # ---------- R04 目录 ↔ 索引 双向 ----------
    idx_set, dir_set = set(by_name), set(dirs)
    for nm in sorted(idx_set - dir_set):
        add("ERROR", "R04", nm, "index.json 里有，但 skills/ 下没有这个目录（或目录缺 SKILL.md）")
    for nm in sorted(dir_set - idx_set):
        add("ERROR", "R04", nm, "skills/ 下有这个目录，但 index.json 里没有登记")

    # ---------- R05 path 字段 ----------
    for nm, e in by_name.items():
        p = e.get("path")
        if not isinstance(p, str):
            continue
        want = f"skills/{nm}"
        if p != want:
            add("ERROR", "R05", nm, f"path 字段应为 {want!r}，实际 {p!r}")
        abs_p = os.path.join(ROOT, p)
        if not os.path.isdir(abs_p):
            add("ERROR", "R05", nm, f"path 指向的目录不存在：{p}")
        elif not os.path.isfile(os.path.join(abs_p, "SKILL.md")):
            add("ERROR", "R05", nm, f"path 指向的目录缺 SKILL.md：{p}")

    # ---------- R06 code 合法性 + 唯一性 ----------
    code_owner: dict[str, list[str]] = defaultdict(list)
    for nm, e in by_name.items():
        code = e.get("code")
        if not isinstance(code, str):
            continue
        if not CODE_RE.match(code):
            add("ERROR", "R06", nm, f"code 必须是 2–3 位大写字母，实际 {code!r}")
        code_owner[code].append(nm)
    for code, owners in sorted(code_owner.items()):
        if len(owners) > 1:
            add("ERROR", "R06", ",".join(owners), f"code {code!r} 被多个 skill 共用")

    # ---------- R07 status ----------
    for nm, e in by_name.items():
        st = e.get("status")
        if isinstance(st, str) and st not in VALID_STATUS:
            add("ERROR", "R07", nm, f"status 应为 {sorted(VALID_STATUS)} 之一，实际 {st!r}")

    # ---------- R09/R10/R11 matrix 三方对齐 ----------
    experts = matrix.get("experts", {}) or {}
    alias = matrix.get("alias_map", {}) or {}
    exp_set = set(experts)
    if exp_set != idx_set:
        for nm in sorted(idx_set - exp_set):
            add("ERROR", "R09", nm, "index.json 有，roundtable-matrix.json 的 experts 里没有")
        for nm in sorted(exp_set - idx_set):
            add("ERROR", "R09", nm, "matrix.experts 有，index.json 里没有")
    if set(alias) != exp_set:
        for nm in sorted(exp_set - set(alias)):
            add("ERROR", "R09", nm, "matrix.alias_map 缺少该 slug 的短代码映射")
        for nm in sorted(set(alias) - exp_set):
            add("ERROR", "R09", nm, "matrix.alias_map 里有，但 experts 里没有")

    for nm in sorted(idx_set & exp_set):
        ie, me = by_name[nm], experts[nm] if isinstance(experts[nm], dict) else {}
        if not isinstance(experts.get(nm), dict):
            add("ERROR", "R09", nm, f"matrix.experts[{nm!r}] 必须是对象")
            continue
        for mfield, ifield in (("person", "person"), ("role", "roundtable_role"),
                               ("path", "path"), ("tags", "roundtable_tags"),
                               ("code", "code")):
            if mfield not in me:
                add("ERROR", "R11", nm, f"matrix.experts 缺字段：{mfield}")
                continue
            if ifield in ie and me[mfield] != ie[ifield]:
                add("ERROR", "R11", nm,
                    f"matrix.experts.{mfield} = {me[mfield]!r} 与 index.{ifield} = {ie[ifield]!r} 不一致")
        if nm in alias and "code" in me and alias[nm] != me["code"]:
            add("ERROR", "R10", nm,
                f"alias_map[{nm!r}] = {alias[nm]!r} 与 experts.code = {me['code']!r} 不一致")

    # ---------- R12 stage 划分 ----------
    stages = matrix.get("stages", {}) or {}
    for st in stages:
        if st not in VALID_STAGES:
            add("ERROR", "R12", st, f"未知阶段名，允许 {sorted(VALID_STAGES)}")
    in_stage: list[str] = []
    for st, members in stages.items():
        if not isinstance(members, list):
            add("ERROR", "R12", st, "阶段成员必须是数组")
            continue
        for nm in members:
            if nm in in_stage:
                add("ERROR", "R12", nm, "同一专家被放进多个阶段")
            in_stage.append(nm)
            if nm not in exp_set:
                add("ERROR", "R12", nm, f"stages[{st!r}] 里引用了不存在的专家")
        me_stage = {nm for nm, v in experts.items()
                    if isinstance(v, dict) and v.get("stage") == st}
        if me_stage != set(members):
            for nm in sorted(me_stage - set(members)):
                add("ERROR", "R12", nm, f"experts.stage={st!r}，但没出现在 stages[{st!r}] 名单里")
            for nm in sorted(set(members) - me_stage):
                add("ERROR", "R12", nm, f"在 stages[{st!r}] 名单里，但 experts.stage 不是该阶段")
    for nm in sorted(exp_set - set(in_stage)):
        add("ERROR", "R12", nm, "没有归属任何阶段")

    # ---------- R13 tag_index 双向 ----------
    tag_index = matrix.get("tag_index", {}) or {}
    expect: dict[str, set[str]] = defaultdict(set)
    for nm, me in experts.items():
        if not isinstance(me, dict):
            continue
        for tag in me.get("tags") or []:
            expect[tag].add(nm)
    for tag in sorted(set(expect) - set(tag_index)):
        add("ERROR", "R13", tag, "有专家带这个标签，但 tag_index 里没有该标签")
    for tag in sorted(set(tag_index) - set(expect)):
        add("ERROR", "R13", tag, "tag_index 里有这个标签，但没有任何专家带它")
    for tag in sorted(set(expect) & set(tag_index)):
        got, want = set(tag_index[tag] or []), expect[tag]
        if got != want:
            for nm in sorted(want - got):
                add("ERROR", "R13", nm, f"带标签 {tag!r}，但 tag_index[{tag!r}] 没列它")
            for nm in sorted(got - want):
                add("ERROR", "R13", nm, f"被 tag_index[{tag!r}] 列出，但 experts.tags 里没有该标签")

    # ---------- R14 版本与日期 ----------
    iv, mv = index.get("version"), matrix.get("version")
    iu, mu = index.get("updated"), matrix.get("updated")
    if iv != mv:
        add("ERROR", "R14", "version", f"index.version = {iv!r} 与 matrix.version = {mv!r} 不一致")
    if iu != mu:
        add("ERROR", "R14", "updated", f"index.updated = {iu!r} 与 matrix.updated = {mu!r} 不一致")
    for label, v in (("index.version", iv), ("matrix.version", mv)):
        if not isinstance(v, str) or not SEMVER_RE.match(v):
            add("ERROR", "R14", label, f"必须是 X.Y.Z 形式，实际 {v!r}")
    for label, v in (("index.updated", iu), ("matrix.updated", mu)):
        if not isinstance(v, str) or not DATE_RE.match(v):
            add("ERROR", "R14", label, f"必须是 YYYY-MM-DD 形式，实际 {v!r}")

    # ---------- R15 frontmatter name 与索引对齐 ----------
    for nm in sorted(idx_set & dir_set):
        fm = frontmatter_name(os.path.join(SKILLS_DIR, nm, "SKILL.md"))
        if fm is None:
            add("ERROR", "R15", nm, "SKILL.md 缺 frontmatter 或缺少 name 字段")
        elif fm != nm:
            add("ERROR", "R15", nm, f"SKILL.md frontmatter name = {fm!r}，与目录/索引名不一致")

    # ---------- R16 逐 skill 版本字段（若索引里出现该字段才校验） ----------
    versioned = [nm for nm, e in by_name.items() if "version" in e]
    if versioned:
        for nm in versioned:
            want = changelog_top_version(nm)
            got = by_name[nm].get("version")
            if want is None:
                add("WARN", "R16", nm, "索引里有 version 字段，但该 skill 的 CHANGELOG.md 无可识别版本号")
            elif str(got) != want:
                add("ERROR", "R16", nm,
                    f"index.version = {got!r} 与该 skill CHANGELOG 最高版本 {want!r} 不一致")
    else:
        add("INFO", "R16", "registry/index.json",
            "索引只有仓库级 version / updated，没有逐 skill 的 version 字段，故不做逐 skill 版本对齐")

    # ---------- R17 被忽略的非 skill 目录 ----------
    for nm in ignored_dirs:
        add("INFO", "R17", f"skills/{nm}",
            "该一级目录下没有 SKILL.md，不计入 skill 数（多为本地未跟踪残留或被 .gitignore 屏蔽）")

    # ---------- R18 complements 引用有效性 ----------
    for nm, e in by_name.items():
        for ref in e.get("complements") or []:
            if ref == nm:
                add("ERROR", "R18", nm, "complements 指向自己")
            elif ref not in idx_set:
                add("ERROR", "R18", nm, f"complements 引用了不存在的 skill：{ref}")

    # ---------- R19 living / died 自洽 ----------
    # living 是 build.py 从 people.py 生成的权威生死标记（True=在世 / False=已故 / None=待考或方法论条目）
    # 校验三点：① 字段必存在；② 取值只能是 true/false/null；③ 已故必须带 died，其余不许带 died。
    for nm, e in by_name.items():
        if "living" not in e:
            add("ERROR", "R19", nm, "缺少 living 字段（应由 build.py 从 people.py 生成）")
            continue
        living, died = e.get("living"), e.get("died")
        if living not in (True, False, None):
            add("ERROR", "R19", nm, f"living 只能是 true/false/null，实际 {living!r}")
        if living is False:
            if not (isinstance(died, str) and died.strip()):
                add("ERROR", "R19", nm, "living=false 但 died 为空（人物状态声明需要卒年）")
        elif died not in (None, ""):
            add("ERROR", "R19", nm, f"living={living!r} 却带 died={died!r}（非已故不应有卒年）")

    # ---------- R20 sources 字段格式 ----------
    # sources 只在查到出处时才填（见 people.py）；这里是格式校验，不要求非空。
    for nm, e in by_name.items():
        if "sources" not in e:
            add("ERROR", "R20", nm, "缺少 sources 字段（应为数组，可为空）")
            continue
        v = e.get("sources")
        if not isinstance(v, list):
            add("ERROR", "R20", nm, f"sources 必须是数组，实际 {type(v).__name__}")
            continue
        bad = [x for x in v if not (isinstance(x, str) and x.strip())]
        if bad:
            add("ERROR", "R20", nm, f"sources 含空值或非字符串元素：{bad!r}")
        if len(set(v)) != len(v):
            add("ERROR", "R20", nm, "sources 含重复项")

    # ---------- R21 registry 与 people.py 字段一致 ----------
    # 这一条防的是最隐蔽的一类漂移：people.py 改了、build.py 却只回填了部分字段，
    # 索引看起来「有内容」但已经是旧的。历史案例：7 个 skill 的 complements 与
    # people.py 不一致，而它们各自的 complements 里还把自己列了进去。
    sys.path.insert(0, os.path.join(ROOT, "tools", "skill-gen"))
    try:
        from people import PEOPLE as _PEOPLE  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        add("INFO", "R21", "tools/skill-gen/people.py",
            f"无法导入 people.py，跳过投影一致性校验（{type(exc).__name__}: {exc}）")
    else:
        proj = {p["name"]: p for p in _PEOPLE}
        mirror = ("person", "domain", "domain_cn", "region", "frameworks",
                  "style_keywords", "roundtable_role", "roundtable_tags", "complements")
        for nm, e in by_name.items():
            p = proj.get(nm)
            if not p:
                continue
            for k in mirror:
                if e.get(k) != p.get(k):
                    add("ERROR", "R21", nm,
                        f"字段 {k} 与 people.py 不一致（索引 {e.get(k)!r} ／ people.py {p.get(k)!r}）")
            if e.get("living") != p.get("living") or e.get("died") != p.get("died"):
                add("ERROR", "R21", nm,
                    f"living/died 与 people.py 不一致（索引 {e.get('living')!r}/{e.get('died')!r}"
                    f" ／ people.py {p.get('living')!r}/{p.get('died')!r}）")

    # ---------- 输出 ----------
    errors = [p for p in problems if p[0] == "ERROR"]
    warns = [p for p in problems if p[0] == "WARN"]
    infos = [p for p in problems if p[0] == "INFO"]

    if args.json:
        print(json.dumps({
            "ok": not errors,
            "skills_in_index": len(by_name),
            "skills_on_disk": len(dirs),
            "ignored_dirs": ignored_dirs,
            "counts": {"error": len(errors), "warn": len(warns), "info": len(infos)},
            "problems": [{"level": l, "check": c, "subject": s, "message": m}
                         for l, c, s, m in problems],
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 72)
        print("registry 漂移校验  registry/index.json + roundtable-matrix.json + skills/")
        print("=" * 72)
        print(f"index.skills 条目数：{len(by_name)}")
        print(f"skills/ 真实 skill 目录数：{len(dirs)}")
        print(f"matrix.experts：{len(experts)}    alias_map：{len(alias)}    tag_index：{len(tag_index)} 个标签")
        print(f"版本：index {iv} ／ matrix {mv}    更新日期：{iu}")
        print("-" * 72)
        for level, check, subject, message in errors + warns + infos:
            print(f"[{level}] {check} {subject} :: {message}")
        if not problems:
            print("（无差异）")
        print("-" * 72)
        print(f"ERROR {len(errors)} ／ WARN {len(warns)} ／ INFO {len(infos)}")
        print("结论：" + ("索引与目录一致 ✅" if not errors else "存在漂移，见上方 ERROR 行 ❌"))

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
