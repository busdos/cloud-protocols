all:
	@echo "[MAKEFILE] Nothing to do. Only rule is 'make tidy_up'"

# Simple rule to tidy up the code
.PHONY: tidy_up
tidy_up:
	@echo "[MAKEFILE] Tidying up the code..."
# black since can't break lines to have \ at the end of the line
# yapf does its own weird things
# black .
# yapf -i -r .
	isort .
	flake8 --max-line-length=60 .
	@echo "[MAKEFILE] Done!"

