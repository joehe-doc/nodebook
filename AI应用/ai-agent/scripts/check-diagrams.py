#!/usr/bin/env python3
"""图表结构校验 —— design-doc-playbook 的机械退出闸门（Phase 3 / Phase 4）。

用法:
    python3 -I scripts/check-diagrams.py docs/design.md [更多.md ...]
    python3 -I scripts/check-diagrams.py --stencils ~/.claude/skills/uml/stencils docs/*.md

校验项（覆盖 PlantUML / DOT 最高频的错误类型）:
    1. fence 标识符合法性     —— ```plantuml|puml|dot|vega-lite|vega|canvas，不能是 ```text/```graphviz
    2. @start*/@end* 配对      —— PlantUML 系
    3. 花括号配对              —— 分组框忘记闭合是最常见的致命错误
    4. 边中引用的别名已定义     —— 别名拼错会静默产生一个空节点
    5. mxgraph 图标名真实存在   —— 凭记忆写的图标名实测失败率 100%，不存在则渲染成空框
    6. graphviz 的 cluster_ 前缀 —— 少了前缀子图不画框
    7. vega 的 $schema          —— 缺失则不渲染
    8. 单图节点数阈值           —— 超过 25 提示拆图（PlantUML 自动布局的舒适区上限）

注意: 本脚本【不等于】渲染验证。布局是否可读、连线是否糊成一团，仍需
      在 Markdown Viewer 里目视检查，或跑 `plantuml -syntax`。

退出码: 0 = 全部通过; 1 = 有 ERROR; 2 = 用法错误
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_FENCES = {"plantuml", "puml", "dot", "vega-lite", "vega", "canvas", "infographic"}
# 这些 fence 本身合法但渲染不出来，是典型的写错
BAD_FENCE_HINTS = {
    "text": "PlantUML/DOT 图必须用 ```plantuml / ```puml / ```dot，```text 不会渲染",
    "graphviz": "graphviz skill 要求用 ```dot，不是 ```graphviz",
    "html": "architecture / infocard skill 要求【直接嵌 HTML】，不能用 ```html 代码块",
    "json": "canvas 用 ```canvas，vega 用 ```vega-lite / ```vega",
    "yaml": "infographic 用空格分隔的 key-value，不是 YAML",
}

PUML_START = re.compile(r"@start(\w+)")
PUML_END = re.compile(r"@end(\w+)")
ICON = re.compile(r"mxgraph\.([a-z0-9_]+)\.([a-z0-9_]+)")
ALIAS_DEF = re.compile(r"\bas\s+([A-Za-z0-9_]+)")
# 一条边: 行首别名 + 连接符 + 目标别名
EDGE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(?:\.\.>|-->|<--|\.\.<|--|->|<-|\.\.|--)\s*(?:[^\s:]+\s*)*?([A-Za-z0-9_]+)")
NODE_LINE = re.compile(r"^\s*(?:mxgraph\.[\w.]+|\w+)\s+\"")
MAX_NODES = 25

# 不参与"边中别名"检查的 PlantUML 关键字
KEYWORDS = {
    "left", "right", "top", "bottom", "direction", "skinparam", "note", "end",
    "rectangle", "package", "cloud", "node", "database", "component", "actor",
    "title", "legend", "endif", "else", "if", "then", "while", "repeat",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.ok: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    def good(self, msg: str) -> None:
        self.ok.append(msg)


def load_stencils(stencil_dir: Path) -> dict[str, str] | None:
    """provider -> 该 provider 的 stencil 文件全文。目录不存在则返回 None（跳过图标校验）。"""
    if not stencil_dir.is_dir():
        return None
    return {p.stem: p.read_text(errors="ignore") for p in stencil_dir.glob("*.md")}


def extract_blocks(text: str) -> list[tuple[str, str, int]]:
    """返回 [(fence, body, 起始行号)]。同时报告可疑的 fence。"""
    blocks: list[tuple[str, str, int]] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^```(\S*)\s*$", lines[i])
        if m:
            fence, start = m.group(1).lower(), i + 1
            body: list[str] = []
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                body.append(lines[i])
                i += 1
            blocks.append((fence, "\n".join(body), start))
        i += 1
    return blocks


def check_plantuml(body: str, where: str, rep: Report, stencils: dict[str, str] | None,
                   max_nodes: int = MAX_NODES) -> None:
    starts = PUML_START.findall(body)
    ends = PUML_END.findall(body)
    if len(starts) != 1 or len(ends) != 1:
        rep.err(where, f"@start/@end 数量异常 (start={len(starts)}, end={len(ends)})，应各为 1")
    elif starts[0] != ends[0]:
        rep.err(where, f"@start{starts[0]} 与 @end{ends[0]} 不匹配")
    else:
        rep.good(f"{where}: @start{starts[0]}/@end{ends[0]} 配对")

    opens, closes = body.count("{"), body.count("}")
    if opens != closes:
        rep.err(where, f"花括号不配对 ({{ ={opens}, }} ={closes}) —— 分组框忘记闭合")
    else:
        rep.good(f"{where}: 花括号配对 {opens}/{closes}")

    # 节点数（粗略：以引号开头的声明行）
    nodes = len(NODE_LINE.findall(body) or re.findall(r"^\s*\S+\s+\"", body, re.M))
    if nodes > max_nodes:
        rep.warn(where, f"节点数约 {nodes} > {max_nodes}，PlantUML 自动布局可能不可读；"
                        f"建议拆成两张图，或改用 graphviz（dot 对大图布局更稳）")
    else:
        rep.good(f"{where}: 节点数 {nodes} ≤ {max_nodes}")

    # 图标名校验
    icons = set(ICON.findall(body))
    if stencils is None:
        if icons:
            rep.warn(where, f"使用了 {len(icons)} 种图标，但未提供 --stencils，跳过存在性校验")
    else:
        bad = []
        for prov, name in sorted(icons):
            content = stencils.get(prov)
            if content is None:
                bad.append(f"mxgraph.{prov}.{name} (无 {prov}.md)")
            elif not re.search(rf"mxgraph\.{prov}\.{re.escape(name)}([^a-z0-9_]|$)", content):
                bad.append(f"mxgraph.{prov}.{name}")
        if bad:
            rep.err(where, f"{len(bad)} 个图标名不存在（会渲染成空框）: " + ", ".join(bad)
                           + "  ← 用 grep 查 ~/.claude/skills/uml/stencils/<provider>.md")
        else:
            rep.good(f"{where}: {len(icons)} 种图标全部存在")

    # 边中别名校验
    aliases = set(ALIAS_DEF.findall(body))
    used: set[str] = set()
    for line in body.split("\n"):
        s = line.strip()
        if not s or s.startswith(("'", "skinparam", "note", "left", "right", "top",
                                  "bottom", "title", "legend", "@")):
            continue
        m = EDGE.match(s)
        if m:
            a, b = m.group(1), m.group(2)
            if a not in KEYWORDS:
                used.add(a)
            if b not in KEYWORDS:
                used.add(b)
    undefined = used - aliases
    if undefined:
        rep.err(where, f"{len(undefined)} 个边中引用的别名未定义（会静默生成空节点）: "
                       + ", ".join(sorted(undefined)))
    else:
        rep.good(f"{where}: 边中 {len(used)} 个别名全部已定义（共 {len(aliases)} 个）")


def check_dot(body: str, where: str, rep: Report) -> None:
    if not re.search(r"\b(digraph|graph)\b", body):
        rep.err(where, "缺少 digraph/graph 声明")
    for m in re.finditer(r"subgraph\s+([A-Za-z0-9_]+)", body):
        name = m.group(1)
        if not name.startswith("cluster_"):
            rep.err(where, f"subgraph {name} 缺少 cluster_ 前缀，不会画成框")
    opens, closes = body.count("{"), body.count("}")
    if opens != closes:
        rep.err(where, f"花括号不配对 ({opens}/{closes})")
    else:
        rep.good(f"{where}: DOT 结构与 cluster_ 前缀检查通过，花括号 {opens}/{closes}")


def check_vega(body: str, where: str, rep: Report) -> None:
    try:
        json.loads(body)
        rep.good(f"{where}: 是合法 JSON")
    except json.JSONDecodeError as e:
        rep.err(where, f"不是合法 JSON: {e}")
    if "$schema" not in body:
        rep.err(where, "缺少 $schema 字段，Vega 不会渲染")
    else:
        rep.good(f"{where}: 含 $schema")


def check_canvas(body: str, where: str, rep: Report) -> None:
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        rep.err(where, f"不是合法 JSON: {e}")
        return
    nodes = data.get("nodes", [])
    missing = [n.get("id", f"index{i}") for i, n in enumerate(nodes)
               if not all(k in n for k in ("id", "x", "y", "width", "height"))]
    if missing:
        rep.err(where, f"节点缺少 id/x/y/width/height: {missing}")
    ids = {n.get("id") for n in nodes}
    bad_edges = [e for e in data.get("edges", [])
                 if e.get("fromNode") not in ids or e.get("toNode") not in ids]
    if bad_edges:
        rep.err(where, f"{len(bad_edges)} 条边引用了不存在的节点 id")
    else:
        rep.good(f"{where}: canvas JSON 合法，{len(nodes)} 节点 / {len(data.get('edges', []))} 边")


def main() -> int:
    ap = argparse.ArgumentParser(description="校验 markdown 中的图表代码块")
    ap.add_argument("files", nargs="+", help="待检查的 markdown 文件")
    ap.add_argument("--stencils", default=str(Path.home() / ".claude/skills/uml/stencils"),
                    help="stencils 目录（用于校验 mxgraph 图标名是否存在）")
    ap.add_argument("--max-nodes", type=int, default=MAX_NODES, help=f"单图节点数阈值（默认 {MAX_NODES}）")
    args = ap.parse_args()

    stencils = load_stencils(Path(args.stencils).expanduser())

    rep = Report()
    if stencils is None:
        rep.warn("(全局)", f"stencils 目录不存在: {args.stencils} —— 跳过图标名校验")
    else:
        rep.good(f"已加载 {len(stencils)} 个 stencil 分类用于图标名校验")

    total_blocks = 0
    for path_str in args.files:
        path = Path(path_str)
        if not path.is_file():
            print(f"ERROR: 文件不存在: {path}", file=sys.stderr)
            return 2
        text = path.read_text(errors="ignore")
        blocks = extract_blocks(text)
        for fence, body, lineno in blocks:
            where = f"{path}:{lineno}"
            if not fence:
                continue
            if fence in BAD_FENCE_HINTS:
                # 报告 fence 错误，但【继续】按推断出的真实类型检查块内内容——
                # 否则用户改完 fence 还要再撞一轮错误
                if re.search(r"@start(uml|mindmap)", body):
                    rep.err(where, f"```{fence} → {BAD_FENCE_HINTS[fence]}")
                    total_blocks += 1
                    check_plantuml(body, where, rep, stencils, args.max_nodes)
                    continue
                if re.search(r"\b(digraph|graph)\b", body):
                    rep.err(where, f"```{fence} → {BAD_FENCE_HINTS[fence]}")
                    total_blocks += 1
                    check_dot(body, where, rep)
                    continue
                if '"$schema"' in body or re.match(r"\s*[\[{]", body):
                    rep.err(where, f"```{fence} → {BAD_FENCE_HINTS[fence]}")
                    total_blocks += 1
                    (check_vega if '"$schema"' in body else check_canvas)(body, where, rep)
                    continue
                continue
            if fence not in VALID_FENCES:
                continue
            total_blocks += 1
            if fence in ("plantuml", "puml"):
                check_plantuml(body, where, rep, stencils, args.max_nodes)
            elif fence == "dot":
                check_dot(body, where, rep)
            elif fence in ("vega", "vega-lite"):
                check_vega(body, where, rep)
            elif fence == "canvas":
                check_canvas(body, where, rep)
            elif fence == "infographic":
                rep.good(f"{where}: infographic 块（模板名需人工对照 skill 的 references/ 清单）")

    print(f"\n检查了 {len(args.files)} 个文件、{total_blocks} 个图表代码块\n")
    if rep.ok:
        print(f"通过 {len(rep.ok)} 项:")
        for m in rep.ok:
            print(f"  ✓ {m}")
    if rep.warnings:
        print(f"\n警告 {len(rep.warnings)} 项:")
        for m in rep.warnings:
            print(f"  ⚠ {m}")
    if rep.errors:
        print(f"\n错误 {len(rep.errors)} 项:")
        for m in rep.errors:
            print(f"  ✗ {m}")
        print("\n结论: 未通过 —— 修复后重跑")
        return 1
    print("\n结论: 通过（但仍需在 Markdown Viewer 中目视确认渲染效果）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
