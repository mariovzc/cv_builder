# AGENTS.md

CV builder: data-driven Harvard-style, ATS-friendly resume generator with a "brutal recruiter" review loop. Python + reportlab, YAML in, PDF out. Public repo — real CV data never leaves `cvs/`.

## Hard rules

- **Everything runs in Docker via `make`** (`make image | cv | check | test | shell`). Never run `python`, `pip` or `pytest` on the host.
- **Never commit personal data.** Real CVs (YAML and PDF) live only in `cvs/`, which is gitignored along with every `*.pdf`. Committed examples use fictional people only (`examples/`).
- **Golden rule of content:** never invent facts, metrics, dates or skills for a CV. Anything unclear — a number, a gap, a keyword — ask the person one question at a time and iterate until it is clear or confirmed unavailable.
- Confidentiality: metrics about a person's current employer go in as approximate orders of magnitude ("hundreds of documents per month"), never exact figures, unless the person states they are public.

## Layout

- `scripts/build_cv.py` — YAML → PDF (one column, Times, EN/ES headings via `lang`, fails if over `max_pages` or text does not extract).
- `scripts/ats_check.py` — standalone ATS sanity check for any existing PDF (intake grading).
- `examples/sample-person.{en,es}.yaml` — fictional person; template, demo and test fixture.
- `cvs/` — real people (gitignored). One YAML per person per language/offer variant: `name.en.yaml`, `name.es.offer-x.yaml`.
- `tests/` — pytest, runs in Docker via `make test`.
- `RECRUITER.md` — **the canonical, agent-agnostic recruiter spec**: intake (parse an existing PDF/Word CV into YAML), interview, generate, grade with the 100-point rubric, iterate until TOP (85+). Any AI assistant working on a CV in this repo follows it. `.claude/skills/cv-recruiter/` is just a thin trigger pointing there for Claude Code.

## Workflow (full spec in RECRUITER.md)

1. Intake: existing PDF/Word → read it, convert to `cvs/<person>.<lang>.yaml`. No CV → interview from scratch.
2. Interview: fill gaps one question at a time (golden rule).
3. Generate: `make cv file=cvs/<person>.<lang>.yaml`.
4. Validate: recruiter grades the result; nothing ships under 85/100.
