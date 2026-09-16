#!/usr/bin/env python3
"""Extract image-based slide decks to per-slide image files.

Usage:
    python3 extract_slide_images.py <deck.pptx|deck.ppt> <outdir>

Why this exists: in an image-based deck every slide is a single full-page
picture, so python-pptx text extraction returns nothing. The only usable
handle on content is the rendered slide image -- one per page.

The slide -> media mapping is resolved through
ppt/slides/_rels/slideN.xml.rels, because the numeric suffix of the media
filename does NOT follow slide order (image7.png may be slide 3).

Output: <outdir>/slideNN.<ext>, NN zero-padded to the width of the page count.
Prints `slides=<N>` on success.
"""
import os
import re
import sys
import zipfile

MEDIA_RE = re.compile(r"media/(image\d+\.(?:png|jpe?g|gif|bmp|emf|wmf|tiff?))", re.I)


def slide_count(z: zipfile.ZipFile) -> int:
    return len([n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)])


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    deck, outdir = sys.argv[1], sys.argv[2]
    if not os.path.isfile(deck):
        print(f"error: no such file: {deck}")
        return 2

    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(deck) as z:
        n = slide_count(z)
        if n == 0:
            print("error: no slides found -- is this a .pptx?")
            return 1
        pad = len(str(n))
        written = 0
        missing = []
        for i in range(1, n + 1):
            try:
                rels = z.read(f"ppt/slides/_rels/slide{i}.xml.rels").decode("utf-8", "replace")
            except KeyError:
                missing.append(i)
                continue
            names = MEDIA_RE.findall(rels)
            if not names:
                missing.append(i)
                continue
            # a slide may embed several images; the full-page render is the
            # largest, so take them all but keep the biggest as slideNN.
            best, best_size = None, -1
            for name in names:
                try:
                    size = z.getinfo(f"ppt/media/{name}").file_size
                except KeyError:
                    continue
                if size > best_size:
                    best, best_size = name, size
            if best is None:
                missing.append(i)
                continue
            ext = os.path.splitext(best)[1].lower()
            dest = os.path.join(outdir, f"slide{str(i).zfill(pad)}{ext}")
            with open(dest, "wb") as fh:
                fh.write(z.read(f"ppt/media/{best}"))
            written += 1

    print(f"slides={n} written={written}")
    if missing:
        print(f"WARNING: no image resolved for slides: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
