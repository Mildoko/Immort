---
name: image-ppt-to-outline
description: Extract outline from image-based PPT decks via vision.
version: 0.1.0
author: Lee Chandler, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [powerpoint, pptx, ocr, vision, outline, transcription]
    related_skills: [powerpoint, docx, obsidian]
---

# Image-PPT-to-Outline Skill

Turns an image-based deck (every slide is one full-page picture, so `python-pptx` text extraction returns nothing) into a faithful page-by-page transcript and a chapter/section outline. Covers detection, slide-to-image mapping, cheap OCR triage, and the vision-model transcription fan-out.

Does not handle text-based decks (use the `powerpoint` skill) and does not OCR scanned PDFs (use the `ocr-and-documents` skill).

## When to Use

- User hands over a `.pptx` / `.ppt` and asks to 提炼大纲 / extract the outline / transcribe it
- `python-pptx` returns slides with **zero text runs** — the tell that the deck is flat images
- You need faithful content (numbers, pricing, ratios) from a deck, not a vibe summary
- Don't use for: text-based decks, one-page images, or PDFs with a real text layer

## Prerequisites

- `pip3 install python-pptx` (required, cross-platform)
- `pip3 install pyobjc-framework-Vision pyobjc-framework-Quartz` (optional, **macOS only**) — powers the fast local OCR triage
- A vision-capable model for `vision_analyze` (the transcription step depends on it; verify by loading one slide before fanning out)

## How to Run

```bash
pip3 install python-pptx --quiet
python3 <skill_dir>/scripts/extract_slide_images.py "<deck.pptx>" /tmp/<deck>_slides
python3 <skill_dir>/scripts/ocr_slides_macos.py /tmp/<deck>_slides   # macOS triage only
```

`<skill_dir>` is the skill directory reported by `skill_view`. `vision_analyze` does the real reading; `delegate_task` does it in parallel.

## Procedure

1. **Confirm the deck is image-based.** Extract text with `python-pptx` (`execute_code`, see Quick Reference). Completion: every slide reports zero non-empty text frames.
2. **Check the shape inventory.** For slide 1 print `shape.shape_type` and `shape.name`. Completion: you can name what the media is — an all-`PICTURE` slide with a name like `*-full-page-slide-*` confirms a flat-image deck.
3. **Map slides to images and extract.** Run `scripts/extract_slide_images.py`. Completion: script prints `slides=<N>` and writes exactly N files named `slideNN.png` / `.jpeg`, one per slide, in **presentation order**.
4. **Triage with local OCR.** Run `scripts/ocr_slides_macos.py` (macOS) or skip. Use it only to locate the TOC page and section dividers cheaply. Completion: you know which page numbers are the TOC and chapter dividers. **Do not treat its text as content** — see Pitfalls 1.
5. **Read the TOC and divider pages yourself** with `vision_analyze` (2–4 pages max). Completion: the official chapter list and their page ranges are written down.
6. **Fan out the per-page transcription.** `delegate_task` with 3 parallel tasks, ~15 slides each, passing absolute image paths. Give every task the same verbatim-transcription contract (see `references/transcription-contract.md`) and the same `output_schema` requiring `transcript_markdown` + `slides_read`. Completion: all three tasks return `status=completed`.
7. **Collect the full transcripts from disk.** Inline summaries are truncated to protect your context — read the saved files under `~/.hermes/<profile>/cache/delegation/subagent-summary-*.txt` and parse the JSON. Completion: `slides_read` for the three tasks sums to the deck's page count.
8. **Synthesize the outline.** Chapter → section → page number → section content (bullets + the concrete numbers). Completion: every page 1..N is accounted for under a chapter or as front/back matter; section count matches the TOC.
9. **Deliver, then offer to archive.** Put the outline in the chat, flag any text that looks like placeholder/fabricated data, and offer to save it as an Obsidian note via the `obsidian` skill if the user works in a vault.

## Quick Reference

```python
# 1. detect: is the deck text-based or image-based?
from pptx import Presentation
prs = Presentation(path)
print(len(prs.slides))
print([sh.shape_type for sh in prs.slides[0].shapes])   # all PICTURE (13) => flat images
# 2. enumerate what text, if any, exists
for i, s in enumerate(prs.slides, 1):
    txt = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    if txt: print(i, txt)
# 3. slide -> media mapping (image index != slide order!)
import re, zipfile
z = zipfile.ZipFile(path)
for i in range(1, n+1):
    rels = z.read(f"ppt/slides/_rels/slide{i}.xml.rels").decode()
    print(i, re.findall(r'media/(image\d+\.\w+)', rels))
```

```bash
python3 scripts/extract_slide_images.py "<deck.pptx>" /tmp/deck_slides
python3 scripts/ocr_slides_macos.py /tmp/deck_slides > /tmp/deck_ocr.txt
```

## Pitfalls

1. **Local OCR lies on decorative fonts.** macOS Vision OCR substitutes whole runs of letters (`Member` → `Mernbor`, `Premium` → `Pr8mlum`) and garbles CJK on stylized type. Its output is good enough to find the TOC page and count chapters, and **useless** for verbatim content. Never quote OCR text as deck content.
2. **Image index is not slide order.** `ppt/media/image7.png` may be slide 3. Always resolve slides through `ppt/slides/_rels/slideN.xml.rels`. Filename sorting silently gives you a shuffled outline.
3. **Extensions vary.** A deck can mix `.png` and `.jpeg` (and `.jpg`, `.emf`). Preserve the original extension; don't assume `.png`.
4. **Read media out of the zip.** A 45-page image deck can be 70 MB+. Don't unzip everything with a shell command — read the needed members in Python.
5. **Subagent summaries are truncated.** The batch result in your context is head+tail only. The complete markdown is on disk — read that file, don't reconstruct from the inline fragment.
6. **Require `slides_read` in the schema.** A child that skips pages looks identical to one that finished. The count is your only cheap audit; reconcile it against the page count.
7. **Verbatim, not summary.** If the contract says "summarize", you lose the numbers, which are the entire value of a deck like a BP. See `references/transcription-contract.md`.
8. **Slide-size sanity.** Very large `prs.slide_width` (e.g. 18288000) means a large-format deck — images are high-res, so vision reads them well without upscaling.

## Verification

- Slide numbers in the transcripts are contiguous 1..N with no gaps, and N equals `len(prs.slides)`.
- The synthesized outline's chapter/section count matches the deck's own TOC page.
- Spot-check three sections (one per subagent batch) against the images yourself — numbers must match the pixels.
- Any claim you cannot see in pixels is either labelled `[不清]` or omitted.

## References

- `references/transcription-contract.md` — the exact per-slide transcription prompt/schema to hand to subagents
