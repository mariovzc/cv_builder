IMAGE := cv-builder
RUN := docker run --rm -v $(CURDIR):/app $(IMAGE)

.PHONY: image cv check test shell

image:
	docker build -q -t $(IMAGE) .

# make cv file=cvs/person.en.yaml  → cvs/person.en.pdf (verified: pages + ATS extraction)
cv: image
	$(RUN) python scripts/build_cv.py $(file)

# make check file=path/to/any.pdf  → ATS sanity check on an existing PDF (intake)
check: image
	$(RUN) python scripts/ats_check.py $(file)

test: image
	$(RUN) pytest -q

shell: image
	docker run --rm -it -v $(CURDIR):/app $(IMAGE) bash
