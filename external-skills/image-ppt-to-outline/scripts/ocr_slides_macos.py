#!/usr/bin/env python3
"""Fast, free, OFFLINE OCR of a folder of slide images via the macOS Vision
framework. macOS only.

Usage:
    python3 ocr_slides_macos.py <imgdir> [out.json]

WHY / WHEN TO USE
    This is a *triage* tool, not a transcription tool. It is fast and free,
    so it is worth running first to locate the table-of-contents page and the
    chapter divider pages before you spend vision-model calls.

    Its output is NOT trustworthy content: on decorative fonts Vision
    substitutes whole runs of letters (Member -> Mernbor, Premium -> Pr8mlum)
    and garbles CJK on stylized type. Never quote this output as deck text.

Requires:
    pip3 install pyobjc-framework-Vision pyobjc-framework-Quartz
"""
import json
import os
import sys

try:
    import Quartz
    import Vision
    from Foundation import NSURL
except ImportError:
    print("error: macOS Vision bindings missing.")
    print("  pip3 install pyobjc-framework-Vision pyobjc-framework-Quartz")
    raise SystemExit(2)

EXTS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")


def ocr(path: str):
    """Return text lines for one image, sorted top-to-bottom then left-to-right."""
    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return None
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if img is None:
        return None

    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(1)          # 0 = fast, 1 = accurate
    req.setRecognitionLanguages_(["zh-Hans", "en-US"])
    req.setUsesLanguageCorrection_(False)  # correction invents words on stylized type
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)

    items = []
    for obs in req.results() or []:
        cands = obs.topCandidates_(1)
        if not cands:
            continue
        bb = obs.boundingBox()
        items.append((bb.origin.y, bb.origin.x, cands[0].string()))
    items.sort(key=lambda t: (-round(t[0], 3), t[1]))
    return [t[2] for t in items]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    imgdir = sys.argv[1]
    if not os.path.isdir(imgdir):
        print(f"error: not a directory: {imgdir}")
        return 2

    files = sorted(f for f in os.listdir(imgdir) if f.lower().endswith(EXTS))
    if not files:
        print(f"error: no images in {imgdir}")
        return 1

    out = {}
    for name in files:
        lines = ocr(os.path.join(imgdir, name))
        out[name] = lines or []
        print(f"===== {name} =====")
        print("\n".join(out[name]))
        print()

    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        print(f"wrote {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
