.PHONY: pdf paper paper-v2 check-paper-v2 check-legacy-paper \
	check-frozen v2-smoke check-v2 clean clean-all clean-root-latex

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PAPER_DIR := $(ROOT_DIR)/paper_v2
PAPER_TEX := main.tex
LEGACY_PAPER_COMMIT := 50cec93
LEGACY_PAPER_TREE := 39e39039f7b65c611815e012310b12978a3f7e5e
LATEXMK ?= latexmk
LATEXMK_FLAGS := -interaction=nonstopmode -halt-on-error -pdf
PYTHON ?= python3

PAPER_ROOT_ARTIFACTS := \
	main.aux \
	main.bbl \
	main.blg \
	main.fdb_latexmk \
	main.fls \
	main.log \
	main.out \
	main.pdf \
	main.spl \
	main.synctex.gz

paper pdf paper-v2: check-legacy-paper
	@cd $(PAPER_DIR) && rm -f $(PAPER_ROOT_ARTIFACTS)
	@cd $(PAPER_DIR) && $(LATEXMK) $(LATEXMK_FLAGS) $(PAPER_TEX)
	@echo "Paper v2 generated: $(PAPER_DIR)/build/main.pdf"

check-paper-v2: paper
	@test -s $(PAPER_DIR)/build/main.pdf
	@scan_status=0; \
	grep -En 'LaTeX Warning:.*undefined|Citation .* undefined|Reference .* undefined|There were undefined references' \
		$(PAPER_DIR)/build/main.log || scan_status=$$?; \
	if [ $$scan_status -eq 0 ]; then \
		echo "Paper v2 contains undefined citations or references."; \
		exit 1; \
	elif [ $$scan_status -ne 1 ]; then \
		echo "Could not scan the Paper v2 log."; \
		exit 1; \
	fi

check-legacy-paper:
	@baseline_tree="$$(git rev-parse $(LEGACY_PAPER_COMMIT):paper)"; \
	if [ "$$baseline_tree" != "$(LEGACY_PAPER_TREE)" ]; then \
		echo "Legacy baseline $(LEGACY_PAPER_COMMIT):paper has unexpected tree $$baseline_tree."; \
		exit 1; \
	fi
	@head_tree="$$(git rev-parse HEAD:paper)"; \
	if [ "$$head_tree" != "$(LEGACY_PAPER_TREE)" ]; then \
		echo "Committed paper/ tree changed: expected $(LEGACY_PAPER_TREE), got $$head_tree."; \
		exit 1; \
	fi
	@if ! git diff --quiet -- paper/; then \
		echo "Legacy paper/ has unstaged changes."; \
		exit 1; \
	fi
	@if ! git diff --cached --quiet -- paper/; then \
		echo "Legacy paper/ has staged changes."; \
		exit 1; \
	fi
	@untracked="$$(git ls-files --others --exclude-standard -- paper/)"; \
	if [ -n "$$untracked" ]; then \
		echo "Legacy paper/ has untracked files:"; \
		echo "$$untracked"; \
		exit 1; \
	fi

check-frozen: check-legacy-paper
	@$(PYTHON) scripts/check_frozen_paths.py

v2-smoke: check-frozen
	@$(PYTHON) -m unittest discover -s experiments/7.4_synthetic_gt -p 'test_*.py' -v
	@$(PYTHON) -m unittest discover -s experiments/8.1_tracetwin -p 'test_*.py' -v
	@$(PYTHON) -m unittest discover -s experiments/8.2_sequential_certificate -p 'test_*.py' -v
	@$(PYTHON) -m unittest discover -s experiments/8.3_agentdojo -p 'test_*.py' -v

check-v2: v2-smoke check-paper-v2

clean-root-latex: clean

clean:
	@cd $(PAPER_DIR) && rm -f $(PAPER_ROOT_ARTIFACTS)
	@cd $(PAPER_DIR) && $(LATEXMK) -C $(PAPER_TEX) || true
	@rm -rf $(PAPER_DIR)/build

clean-all: clean
