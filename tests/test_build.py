import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def build(yaml_name, tmp_path):
    out = tmp_path / f"{yaml_name}.pdf"
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_cv.py"),
         str(ROOT / "examples" / yaml_name), "-o", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    return out


@pytest.mark.parametrize("yaml_name,heading", [
    ("sample-person.en.yaml", "PROFESSIONAL EXPERIENCE"),
    ("sample-person.es.yaml", "EXPERIENCIA PROFESIONAL"),
])
def test_build_is_one_page_and_ats_readable(yaml_name, heading, tmp_path):
    out = build(yaml_name, tmp_path)
    reader = PdfReader(str(out))
    text = "\n".join(p.extract_text() or "" for p in reader.pages)
    assert len(reader.pages) == 1
    assert len(text.split()) > 100, "text must be extractable for an ATS"
    assert heading in text
    assert "Sam Rivera".upper() in text.upper()


def test_bold_markdown_does_not_leak(tmp_path):
    out = build("sample-person.en.yaml", tmp_path)
    reader = PdfReader(str(out))
    text = "\n".join(p.extract_text() or "" for p in reader.pages)
    assert "**" not in text


def test_ats_check_passes_on_built_pdf(tmp_path):
    out = build("sample-person.en.yaml", tmp_path)
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ats_check.py"), str(out),
         "--max-pages", "1"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout
