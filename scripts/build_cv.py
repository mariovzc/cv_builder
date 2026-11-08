#!/usr/bin/env python3
"""Build a Harvard-style, ATS-friendly resume PDF from a YAML file.

Usage: python scripts/build_cv.py cvs/person.en.yaml [-o out.pdf]

ATS constraints enforced: single column, no graphics, standard section
headings (EN/ES via `lang`), Times family, real extractable text, page
limit (`max_pages`, default 1). The build fails if the PDF breaks them.
"""
import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import yaml
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

HEADINGS = {
    "en": {
        "summary": "SUMMARY",
        "experience": "PROFESSIONAL EXPERIENCE",
        "education": "EDUCATION",
        "certifications": "CERTIFICATIONS",
        "skills": "TECHNICAL SKILLS",
    },
    "es": {
        "summary": "RESUMEN",
        "experience": "EXPERIENCIA PROFESIONAL",
        "education": "EDUCACIÓN",
        "certifications": "CERTIFICACIONES",
        "skills": "HABILIDADES TÉCNICAS",
    },
}


def rich(text):
    """Escape user text for reportlab, keeping **bold** markdown."""
    out = escape(str(text))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)


def build(data, out_path):
    doc = SimpleDocTemplate(
        str(out_path), pagesize=letter,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
        title=f"{data['name']} - Resume",
        author=data["name"],
        subject=data.get("headline", ""),
    )
    W = doc.width
    h = HEADINGS[data.get("lang", "en")]

    name_st = ParagraphStyle("name", fontName="Times-Bold", fontSize=16,
                             leading=19, alignment=TA_CENTER, spaceAfter=3)
    headline_st = ParagraphStyle("headline", fontName="Times-Bold", fontSize=11,
                                 leading=13, alignment=TA_CENTER, spaceAfter=2)
    contact_st = ParagraphStyle("contact", fontName="Times-Roman", fontSize=9.5,
                                leading=12, alignment=TA_CENTER)
    section_st = ParagraphStyle("section", fontName="Times-Bold", fontSize=10.5,
                                leading=12, spaceBefore=6, spaceAfter=1)
    body_st = ParagraphStyle("body", fontName="Times-Roman", fontSize=10,
                             leading=11.7, alignment=TA_JUSTIFY)
    bullet_st = ParagraphStyle("bullet", parent=body_st, leftIndent=14,
                               bulletIndent=4, spaceAfter=1)
    note_st = ParagraphStyle("note", parent=body_st, fontName="Times-Italic",
                             spaceAfter=2)

    def section(title):
        return [
            Paragraph(title, section_st),
            HRFlowable(width="100%", thickness=0.7, color=colors.black,
                       spaceBefore=0, spaceAfter=3),
        ]

    def row(left, right):
        t = Table(
            [[Paragraph(left, body_st),
              Paragraph(f'<para alignment="right">{right}</para>', body_st)]],
            colWidths=[W * 0.72, W * 0.28],
        )
        t.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return t

    story = [Paragraph(escape(data["name"].upper()), name_st)]
    if data.get("headline"):
        story.append(Paragraph(rich(data["headline"]), headline_st))
    for line in data.get("contact", []):
        story.append(Paragraph(rich(line), contact_st))
    story.append(Spacer(1, 4))

    if data.get("summary"):
        story += section(h["summary"])
        story.append(Paragraph(rich(data["summary"]), body_st))

    if data.get("experience"):
        story += section(h["experience"])
        for i, job in enumerate(data["experience"]):
            if i:
                story.append(Spacer(1, 4))
            story.append(row(f"<b>{escape(job['company'])}</b> — {escape(job['role'])}",
                             f"<b>{escape(job['dates'])}</b>"))
            if job.get("note"):
                story.append(Paragraph(rich(job["note"]), note_st))
            for b in job.get("bullets", []):
                story.append(Paragraph(rich(b), bullet_st, bulletText="•"))

    for key in ("education", "certifications"):
        if data.get(key):
            story += section(h[key])
            for e in data[key]:
                story.append(row(rich(e["item"]), escape(str(e.get("dates", "")))))

    if data.get("skills"):
        story += section(h["skills"])
        for s in data["skills"]:
            story.append(Paragraph(f"<b>{escape(s['label'])}:</b> {rich(s['items'])}",
                                   ParagraphStyle("skill", parent=body_st,
                                                  alignment=0, spaceAfter=1)))

    doc.build(story)


def verify(out_path, max_pages):
    reader = PdfReader(str(out_path))
    pages = len(reader.pages)
    text = "\n".join((p.extract_text() or "") for p in reader.pages).strip()
    words = len(text.split())
    problems = []
    if not text or words < 50:
        problems.append(f"ATS FAIL: only {words} extractable words")
    if pages > max_pages:
        problems.append(f"FAIL: {pages} pages (max {max_pages})")
    return pages, words, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml_file")
    ap.add_argument("-o", "--output", help="output PDF (default: alongside the YAML)")
    args = ap.parse_args()

    src = Path(args.yaml_file)
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    out = Path(args.output) if args.output else src.with_suffix(".pdf")

    build(data, out)
    pages, words, problems = verify(out, int(data.get("max_pages", 1)))

    print(f"{out} — pages: {pages}, extractable words: {words}")
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
