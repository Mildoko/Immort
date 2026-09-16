# Transcription contract (hand this to every `delegate_task` child)

The whole value of a deck transcription is **verbatim content and numbers**. A
child that summarizes destroys the deliverable. Use the block below as the
`context` for each batch task, filling in the page range and filenames.

## Context block for each child

```
待转录的幻灯片图片位于本地目录 <SLIDE_DIR>/，文件名格式为 slide01.png ~ slideNN.png
（注意扩展名可能是 .jpeg，以实际文件为准）。

这是 <ONE-LINE PROJECT DESCRIPTION: what the deck is, who it's for, language mix>。

你的任务：对 <SLIDE_DIR>/slide<A>.<ext> 到 slide<B>.<ext> 逐页调用
vision_analyze(image_url=<该页绝对路径>,
  question="忠实逐字转录本页全部文字（中英文都要），保留标题层级；图表请说明数值与含义；不要总结")，
然后用你自己看到的画面内容，把每一页完整写成如下结构：

## 第 N 页
**标题：**（原文标题，中英照抄）
**版式：**（如封面/目录/图表页/手机截图页/后台截图页）
**文字内容：**
- 逐条列出页面上所有可见文字，保留原有层级（大标题/小标题/正文/标签/按钮文字/数据标签）。
**图表与数据：**
- 如有图表、数据看板、数字指标，列出具体数值、单位、百分比、维度名称。
**要点：**
- 一句话说明这页在论证什么。

严禁总结代替转录，严禁编造。看不清的地方写「[不清]」。图片必须逐页真实打开查看，不要跳过任何一页。
```

## Required output_schema

```json
{
  "type": "object",
  "properties": {
    "transcript_markdown": {"type": "string", "description": "本批页面的完整 markdown 转录"},
    "slides_read": {"type": "integer"}
  },
  "required": ["transcript_markdown", "slides_read"],
  "description": "第 A–B 页的完整转录"
}
```

`slides_read` is the audit hook: reconcile the three batches' counts against
`len(prs.slides)`. A silent skip is otherwise indistinguishable from success.

## Batching

- Up to 3 children in parallel; ~15 pages each for a 45-page deck.
- Keep batches contiguous and non-overlapping so page numbers stay traceable.
- Pass the same contract verbatim to all children — differing wording produces
  inconsistent structure and makes the later synthesis harder.
- State the one-line project description: without it a child misreads
  abbreviations and product names.

## Collecting results

The batch result that re-enters the parent context is **head+tail truncated**.
Do not reconstruct from it. Read the complete summaries from disk instead:

```python
import json, glob
for f in sorted(glob.glob("~/.hermes/*/cache/delegation/subagent-summary-*_*.txt")):
    raw = open(f).read().strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rstrip()
        if raw.endswith("```"):
            raw = raw[:-3]
    print(json.loads(raw)["transcript_markdown"])
```

Printed output is capped (~50 KB), so page through one file at a time when
several are large.

## Synthesis rules

- Keep the deck's own vocabulary for section titles — do not rename chapters.
- Keep every number the child captured: prices, ratios, percentages, headcounts,
  valuations, dates. They are the reason the transcription exists.
- Mark questionable content explicitly. Decks routinely show demo/placeholder
  dashboards; flag those numbers as "该页为演示/示意数据，未经核实" rather than
  presenting them as facts.
- Preserve `[不清]` markers instead of guessing.
