#!/usr/bin/env python3
"""ATS sanity check for any resume PDF (intake grading).

Usage: python scripts/ats_check.py resume.pdf [--max-pages 2]
Exit 0 = pass, 1 = fail. Prints findings + the text an ATS would see.
"""
import argparse
import sys

from pypdf import PdfReader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--max-pages", type=int, default=2)
    args = ap.parse_args()

    reader = PdfReader(args.pdf)
    pages = len(reader.pages)
    text = "\n".join((p.extract_text() or "") for p in reader.pages).strip()
    words = len(text.split())

    fails = []
    if not text:
        fails.append("CRITICAL: no extractable text — an ATS reads an empty CV")
    elif words < 100:
        fails.append(f"CRITICAL: only {words} extractable words — text likely lives in images")
    if pages > args.max_pages:
        fails.append(f"FAIL: {pages} pages (max {args.max_pages})")

    has_images = any(p.images for p in reader.pages)

    print(f"pages: {pages}")
    print(f"extractable words: {words}")
    print(f"embedded images: {'yes (check they hold no text)' if has_images else 'no'}")
    for f in fails:
        print(f)
    print("\n--- TEXT AN ATS SEES ---")
    print(text[:6000])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
