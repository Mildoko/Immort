#!/usr/bin/env python3
"""交互案文档集审计 —— 六项机械一致性检查，退出码 0 = 通过。

用法：
    python3 audit_interaction_docs.py <文档目录> [规范文件名] [交互案文件名]

默认按「一份美术规范 + 一份交互案」的文档集工作：
    <目录>/03_UI设计规范.md     ← 取值的唯一定义源
    <目录>/04_交互案.md         ← 界面清单 + 逐界面提示词

六项检查：
    [1] 界面覆盖      —— 规范清单声明的界面 ↔ 交互案实际交付的章节，双向求差
    [2] 入口/出口     —— 每个界面章节都要有「入口（上游）」与「出口（下游）」
    [3] 跳转死链      —— 跳转映射表的「终点」列不得指向不存在的界面
    [4] 孤儿界面      —— 每个界面都要能从别处到达
    [5] 取值闭环      —— 交互案提示词里用到的每个 HEX，规范必须定义过
    [6] 命名一致性    —— 界面名在规范清单与交互案章节标题里逐字一致

为什么必须脚本化（详见 SKILL.md §5.1–5.4）：
    ① 「取值闭环」要把提示词里每一个 HEX 回查规范 —— 漏掉的往往正好落在已定义值旁边，
       看着「差不多」就放过了，肉眼绝无可能发现；
    ② 「命名一致性」差一个括号或空格就会误判；
    ③ 每改一次文档都要重跑，人工不可能每次全量过一遍。

严重级（不要改）：
    「用了但没定义」= 硬错误 → 计入 FAIL，退出码 1
    「定义但没用」  = 冗余   → 只作提示，不计入 FAIL
    把非错误当失败，工具就会被绕过。

适配要点（若你的文档结构不同）：
    · SCREEN_RE —— 界面 ID 的正则，默认匹配 S01/S02…
    · 章节标题约定 —— 默认 `### <编号> <界面ID> <名称>`，改 SECTION_RE
    · 跳转表的「终点」列 —— 默认按表头 `J号|起点|触发|终点|落地页|返回|传参` 取 cols[2]。
      解析表格前先数一遍表头，列索引写错会让整表报「无法解析」并连带误判孤儿。
    · 命名比对先剥括注 —— 规范写「X（实现细节）」、交互案写「X（L1 · 副标题）」是正常的，
      取括号前主名再比，否则全是误报。
"""
import re
import sys
from pathlib import Path

BASE = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SPEC = BASE / (sys.argv[2] if len(sys.argv) > 2 else "03_UI设计规范.md")
INTER = BASE / (sys.argv[3] if len(sys.argv) > 3 else "04_交互案.md")

SCREEN_RE = r"S\d{2}"                                  # 界面 ID 形态
SECTION_RE = re.compile(rf"^### \d+(?:\.\d+)?\s+({SCREEN_RE})\s+(.+)$", re.M)
# 合法的「根」界面：启动页（无入边）/ 唯一主界面 / 组件组（非页面）—— 按项目填写
ROOTS = {"S01", "S03", "S20"}

spec = SPEC.read_text(encoding="utf-8")
inter = INTER.read_text(encoding="utf-8")
fails = []


def check(label, bad, ok_note=""):
    if bad:
        fails.append(label)
        print(f"  ✗ {label}：{bad}")
    else:
        print(f"  ✓ {label}{(' ' + ok_note) if ok_note else ''}")


print("=" * 62)
print(f"文档集审计 —— {BASE}")
print("=" * 62)

# ── [1] 界面覆盖 ────────────────────────────────────────────────────
listed = set(re.findall(rf"\|\s*({SCREEN_RE})\s*\|", spec))          # 规范清单
delivered = {m.group(1) for m in SECTION_RE.finditer(inter)}        # 交互案章节
print(f"\n[1] 界面覆盖   规范清单 {len(listed)} · 实际交付 {len(delivered)}")
check("清单里有但没写", sorted(listed - delivered))
check("写了但清单里没有", sorted(delivered - listed))

# ── [2] 入口 / 出口 完整性 ──────────────────────────────────────────
print(f"\n[2] 入口/出口 完整性")
sections = re.split(rf"^### \d+(?:\.\d+)?\s+", inter, flags=re.M)[1:]
no_io = []
for sec in sections:
    m = re.match(rf"({SCREEN_RE})", sec)
    if m and ("入口（上游）" not in sec[:1800] or "出口（下游）" not in sec[:1800]):
        no_io.append(m.group(1))
check("缺入口或出口的界面", no_io, f"（共 {len(sections)} 个章节）")

# ── [3] 跳转死链 ────────────────────────────────────────────────────
print(f"\n[3] 跳转死链")
jrows = re.findall(r"^\|\s*(J\d+)\s*\|(.+)$", inter, re.M)           # 跳转映射表
targets, unparsed = set(), []
for jid, rest in jrows:
    cols = rest.split("|")
    if len(cols) < 3:
        continue
    dest = cols[2]                                                   # ← 终点列（表头第 3 个字段）
    found = re.findall(rf"\b({SCREEN_RE})\b", dest)
    if not found and not any(k in dest for k in ("无跳转", "原地", "停", "按规则")):
        unparsed.append(f"{jid}→{dest.strip()}")
    targets |= set(found)
check("指向不存在的界面", sorted(targets - listed - delivered))
check("终点无法解析", unparsed)
print(f"  · 跳转条目 {len(jrows)} 条 ⟶ 解析出目标 {len(targets)} 个")

# ── [4] 孤儿界面 ────────────────────────────────────────────────────
print(f"\n[4] 孤儿界面")
check("无任何入口指向的界面", sorted(delivered - targets - ROOTS), f"（共 {len(delivered)} 个）")

# ── [5] 取值闭环 ────────────────────────────────────────────────────
print(f"\n[5] 取值闭环（HEX）")
hex_spec = {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{6}", spec)}
hex_inter = {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{6}", inter)}
print(f"  规范定义 {len(hex_spec)} · 交互案使用 {len(hex_inter)}")
check("用了但规范未定义的颜色", sorted(hex_inter - hex_spec))          # 硬错误
print(f"  · 定义但全案未使用（冗余，非失败）：{sorted(hex_spec - hex_inter) or '无'}")


# ── [6] 命名一致性 ──────────────────────────────────────────────────
print(f"\n[6] 命名一致性")
def base_name(s: str) -> str:
    """剥掉粗体标记与括注，只留主名。规范与交互案的括注内容天然不同，比括注必然误报。"""
    return re.split(r"[（(]", re.sub(r"[*`]", "", s))[0].strip()


spec_names = {m.group(1): base_name(m.group(2))
              for m in (re.match(rf"\|\s*({SCREEN_RE})\s*\|\s*(.+?)\s*\|", ln) for ln in spec.splitlines()) if m}
inter_names = {m.group(1): base_name(m.group(2)) for m in SECTION_RE.finditer(inter)}
mismatch = [f"{sid}: 规范「{spec_names[sid]}」≠ 交互案「{inter_names[sid]}」"
            for sid in sorted(set(spec_names) & set(inter_names))
            if spec_names[sid] != inter_names[sid]]
check("两处界面名对不上", mismatch, f"（比对 {len(inter_names)} 个）")

# ── 汇总 ────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
if fails:
    print(f"❌ FAIL —— {len(fails)} 项未通过：{' / '.join(fails)}")
    sys.exit(1)
print("✅ PASS —— 界面覆盖 / 入口出口 / 跳转 / 孤儿 / 取值闭环 / 命名一致性 全部通过")
sys.exit(0)
