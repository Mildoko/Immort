#!/usr/bin/env python3
"""STE100 中文文档集结构化自检 / 改造辅助（stdlib only）。

三个模式：

  1) 扫描（默认）
     python3 ste_scan_cn.py <路径...> [--json] [--baseline N] [--max-cjk 40]
                            [--no-exempt-prompt] [--disable rule1,rule2]

  2) 列出 / 就地重排「行内压缩规格」（模块卡片）
     python3 ste_scan_cn.py --module-cards FILE.md          # 只列出行号
     python3 ste_scan_cn.py --restructure-module-cards FILE  # 就地重排（幂等）

  3) 验证零丢失（token 多重集 diff）
     python3 ste_scan_cn.py --loss-check OLD.md NEW.md

扫描规则名（用于 --disable）：
  semicolon-prose   散文里的中文分号        —— STE 8.1 硬禁
  semicolon-table   表格单元格里的分号      —— 本工作区规矩：改 <br>
  long-sentence     散文里的超长句（默认 >40 CJK 字）
  marketing         营销形容词
  nominalization    名词化结构（进行…的分析）
  dangling-conj     列表项末尾的悬空连词（以及/和/或者/and/or）
  paren-period      括号内部的句号 —— 通常是 ；->。 机械替换的副作用

豁免（不计入、不修改）：代码围栏内、行内 code、图像生成提示词块。

退出码：硬违规总数 > --baseline 时返回 1。
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

CJK = re.compile(r"[\u4e00-\u9fff]")
INLINE = re.compile(r"`[^`]*`")
HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b")

MARKETING = ["无缝", "强大", "领先", "一站式", "极致", "彻底", "全面", "完美",
             "智能", "卓越", "高效", "一站式服务",
             "seamless", "robust", "powerful", "cutting-edge", "effortless", "blazing"]

NOMINAL = [r"进行[^，。；]{0,8}(?:分析|评估|处理|优化|验证|统计)",
           r"作出[^，。；]{0,8}(?:判断|决定|选择)",
           r"予以", r"给予[^，。；]{0,4}(?:支持|帮助)",
           r"提供[^，。；]{0,4}(?:协助|帮助)"]

DANGLING = re.compile(r"^\s*(?:[-*+]|\d+[.、])\s.*(?:以及|和|或者|and|or)\s*$")

# 图像生成提示词块的识别特征：引用块 + 视觉描述标记
PROMPT_HINT = ("扁平风格", "无 3D", "无3D", "手机竖屏", "界面 UI", "界面UI", "弹窗",
               "游戏界面", "游戏结算页", "像素", "px", "直径", "插画", "立绘")

MODULE_RE = re.compile(r"^(- \*\*模块[^\n]*?\*\*)\s*—\s*(.*?)\s*/\s*\*\*作用\*\*：(.*)$")

HARD_RULES = {"semicolon-prose", "semicolon-table", "long-sentence",
              "marketing", "dangling-conj", "nominalization", "paren-period"}


def strip_inline(line):
    return INLINE.sub("", line)


def is_prompt_block(line):
    s = line.strip()
    if not s.startswith(">"):
        return False
    if HEX.search(s) and any(k in s for k in PROMPT_HINT):
        return True
    return any(k in s for k in ("手机竖屏", "扁平风格", "无 3D")) and "界面" in s


def iter_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for dp, _dn, fn in os.walk(p):
                if ".git" in dp.split(os.sep):
                    continue
                for f in sorted(fn):
                    if f.endswith((".md", ".markdown", ".mdx")):
                        out.append(os.path.join(dp, f))
        elif os.path.isfile(p):
            out.append(p)
        else:
            print("skip (not found): %s" % p, file=sys.stderr)
    return out


def find_long_sentence(line, max_cjk):
    """Returns True if any sentence in the stripped line exceeds max_cjk CJK chars."""
    for seg in re.split(r"[。！？!?]", line):
        if len(CJK.findall(seg)) > max_cjk:
            return True
    return False


def scan_file(path, max_cjk, exempt_prompt, disabled):
    findings = []
    in_fence = False
    with open(path, encoding="utf-8") as fh:
        for i, raw in enumerate(fh.read().split("\n"), 1):
            s = raw.strip()
            if s.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if exempt_prompt and is_prompt_block(raw):
                continue

            body = strip_inline(raw)
            is_table = s.startswith("|")

            # 分号（STE 8.1 全禁；位置决定改法）
            semi = body.count("；")
            if semi:
                rule = "semicolon-table" if is_table else "semicolon-prose"
                if rule not in disabled:
                    findings.append((rule, i, "%d 处「；」" % semi, raw[:90]))
            if is_table:
                continue

            if "long-sentence" not in disabled and find_long_sentence(body, max_cjk):
                findings.append(("long-sentence", i, ">%d 字" % max_cjk, raw[:90]))

            for w in MARKETING:
                if w in body:
                    findings.append(("marketing", i, w, raw[:90]))
                    break

            for pat in NOMINAL:
                if re.search(pat, body):
                    findings.append(("nominalization", i, pat, raw[:90]))
                    break

            if DANGLING.match(raw):
                findings.append(("dangling-conj", i, "列表项末尾悬空连词", raw[:90]))

            # 括号内句号 = ；->。 机械替换的典型副作用
            if "paren-period" not in disabled and re.search(r"（[^（）]*。", body):
                findings.append(("paren-period", i, "括号内含句号", raw[:90]))
    return findings


def do_scan(paths, args):
    files = iter_files(paths)
    disabled = set(x for x in (args.disable or "").split(",") if x)
    per_file = {}
    totals = Counter()
    for p in files:
        f = scan_file(p, args.max_cjk, not args.no_exempt_prompt, disabled)
        if f:
            per_file[p] = f
            for rule, _ln, _d, _t in f:
                totals[rule] += 1

    hard = sum(v for k, v in totals.items() if k in HARD_RULES)
    if args.json:
        print(json.dumps({"files": len(files), "totals": dict(totals),
                          "hard": hard, "details": {
                              k: [{"rule": r, "line": ln, "detail": d}
                                  for r, ln, d, _t in v] for k, v in per_file.items()}},
                         ensure_ascii=False, indent=1))
    else:
        for p, f in per_file.items():
            print("%s" % p)
            by_rule = {}
            for rule, ln, d, t in f:
                by_rule.setdefault(rule, []).append(ln)
            for rule, lns in sorted(by_rule.items()):
                shown = ",".join(str(x) for x in lns[:20])
                more = "" if len(lns) <= 20 else " (+%d)" % (len(lns) - 20)
                print("    %-18s %3d 行: %s%s" % (rule, len(lns), shown, more))
        print("\n合计: " + (" · ".join("%s=%d" % (k, v) for k, v in sorted(totals.items())) or "无违规"))
        print("硬违规总数: %d   baseline: %d" % (hard, args.baseline))
    return 1 if hard > args.baseline else 0


def restructure_module_card(line):
    m = MODULE_RE.match(line)
    if not m:
        return None
    head, content, effects = m.groups()
    out = [head]
    cps = [c.strip() for c in content.split("；") if c.strip()]
    if len(cps) > 1:
        out.append("  - **内容**：")
        out += ["    - " + c for c in cps]
    else:
        out.append("  - **内容**：" + cps[0])
    out.append("  - **作用**：")
    out += ["    - " + e.strip() for e in effects.split("；") if e.strip()]
    return "\n".join(out)


def do_module_cards(path, apply_in_place):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    hits = [i for i, l in enumerate(lines) if MODULE_RE.match(l)]
    if not hits:
        print("no module-card lines found in %s" % path)
        return 0
    if not apply_in_place:
        for i in hits:
            print("%d: %s" % (i + 1, lines[i][:100]))
        print("\n%d 行可重排。加 --restructure-module-cards 就地应用。" % len(hits))
        return 0
    for i in hits:                       # 就地应用；每行独立替换，无需倒序
        lines[i] = restructure_module_card(lines[i])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("已重排 %d 行: %s" % (len(hits), path))
    return 0


TOKEN_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z_]+|\d+(?:\.\d+)?")


def tokens(text):
    return Counter(TOKEN_RE.findall(INLINE.sub("", text)))


def do_loss_check(old_path, new_path):
    with open(old_path, encoding="utf-8") as fh:
        old = fh.read()
    with open(new_path, encoding="utf-8") as fh:
        new = fh.read()
    co, cn = tokens(old), tokens(new)
    lost = {k: co[k] - cn.get(k, 0) for k in co if co[k] > cn.get(k, 0)}
    added = {k: cn[k] - co.get(k, 0) for k in cn if cn[k] > co.get(k, 0)}
    print("old=%d chars  new=%d chars" % (len(old), len(new)))
    print("\n减少的 token（必须全部可解释）:")
    for k, v in sorted(lost.items(), key=lambda x: -x[1])[:60]:
        print("  -%d  %s" % (v, k))
    if not lost:
        print("  (none)")
    print("\n新增的 token:")
    for k, v in sorted(added.items(), key=lambda x: -x[1])[:60]:
        print("  +%d  %s" % (v, k))
    if not added:
        print("  (none)")
    print("\n提示: 单字符差异多为句子重切引起的 token 边界重排，属正常；"
          "成段 CJK 串消失才需要回查。")


def main():
    ap = argparse.ArgumentParser(description="STE100 中文文档集结构化自检")
    ap.add_argument("paths", nargs="*", help="文件或目录")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline", type=int, default=0)
    ap.add_argument("--max-cjk", type=int, default=40)
    ap.add_argument("--no-exempt-prompt", action="store_true",
                    help="不豁免图像生成提示词块（默认豁免）")
    ap.add_argument("--disable", default="", help="逗号分隔的规则名")
    ap.add_argument("--module-cards", metavar="FILE")
    ap.add_argument("--restructure-module-cards", metavar="FILE")
    ap.add_argument("--loss-check", nargs=2, metavar=("OLD", "NEW"))
    args = ap.parse_args()

    if args.loss_check:
        do_loss_check(*args.loss_check)
        return 0
    if args.module_cards:
        return do_module_cards(args.module_cards, False)
    if args.restructure_module_cards:
        return do_module_cards(args.restructure_module_cards, True)
    if not args.paths:
        ap.print_help()
        return 2
    return do_scan(args.paths, args)


if __name__ == "__main__":
    sys.exit(main())
