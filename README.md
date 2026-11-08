# cv_builder

Data-driven resume builder with a built-in "brutal recruiter" review loop.
YAML in → Harvard-style, ATS-friendly PDF out → a merciless technical recruiter
(a Claude Code skill) grades it on a 100-point rubric and interviews you until
it reaches the top of the stack.

Everything runs in Docker. No personal data is ever committed: real CVs live in
`cvs/`, which is gitignored.

## Quick start

```bash
make test                                      # build image + run tests
make cv file=examples/sample-person.en.yaml    # demo: fictional person → PDF
```

Your own CV:

```bash
cp examples/sample-person.en.yaml cvs/me.en.yaml
# edit cvs/me.en.yaml with your data
make cv file=cvs/me.en.yaml                    # → cvs/me.en.pdf
```

The build fails if the PDF exceeds `max_pages` or its text is not extractable —
the two ways a resume silently dies inside an ATS.

Check any existing PDF the way an ATS sees it:

```bash
make check file=path/to/old-resume.pdf
```

## The recruiter loop (Claude Code)

Open this repo in [Claude Code](https://claude.com/claude-code) and say
*"improve my CV"* (or *"mejora mi hoja de vida"* — it works in Spanish and
English). The bundled `cv-recruiter` skill will:

1. **Intake** — read your existing PDF/Word CV and convert it to YAML, or
   interview you from scratch.
2. **Interview** — anything unclear (a metric, a gap, a keyword) gets asked
   one question at a time. The golden rule: facts are never invented.
3. **Generate** — `make cv`, Harvard format: one column, Times, standard
   headings (English or Spanish — the person picks per job offer), 1 page.
4. **Grade** — a 6-second scan plus a 100-point rubric (quantified impact,
   keywords, ATS format, clarity, trajectory, basics). Verdicts range from
   REJECTED to TOP OF THE STACK. Nothing ships under 85.
5. **Iterate** — fix, regenerate, regrade.

## YAML schema

See `examples/sample-person.en.yaml` (English) and `sample-person.es.yaml`
(Spanish). `lang` switches the section headings; `**bold**` works inside
bullets; one YAML per person per language or job-offer variant.

## Commands

| Command | What it does |
|---|---|
| `make cv file=<yaml>` | Build + verify a resume PDF |
| `make check file=<pdf>` | ATS sanity check on any PDF |
| `make test` | Run the test suite |
| `make shell` | Shell inside the container |
