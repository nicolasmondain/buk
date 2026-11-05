PY ?= python3
SKILL := skills/buk
DEMO := flashs/dague-coeur

# Toutes les cibles commencent par buk- (le « : » est réservé par make).
.PHONY: buk-help buk-link buk-test buk-demo buk-classiques buk-motifs buk-package \
        buk-research-list buk-research-fetch buk-coverage buk-clean

buk-help:
	@echo "make buk-link            relie le skill pour Claude Code (.claude/skills/buk)"
	@echo "make buk-test            tests de bout en bout"
	@echo "make buk-demo            régénère le flash d'exemple dague-cœur et ses calques"
	@echo "make buk-classiques      régénère la bibliothèque de vrais flashs (images CC0 requises)"
	@echo "make buk-motifs          régénère les pièces dessinées et leurs planches"
	@echo "make buk-package         dist/buk.zip à importer dans claude.ai (Skills)"
	@echo "make buk-research-list   catalogue les vidéos (research/sources.yaml)"
	@echo "make buk-research-fetch  transcrit un lot de 5 vidéos (s'arrête si couverture atteinte)"
	@echo "make buk-coverage        état de la couverture de recherche"
	@echo "make buk-clean           supprime dist/ et les caches"

buk-link:
	mkdir -p .claude/skills && rm -f .claude/skills/buk && ln -sfn ../../skills/buk .claude/skills/buk
	@echo ".claude/skills/buk -> skills/buk"

buk-test:
	$(PY) -m unittest discover -s tests -v

buk-demo:
	$(PY) $(SKILL)/assets/flash/_generer_dague_coeur.py
	mkdir -p $(DEMO)
	cp $(SKILL)/assets/flash/dague_coeur.svg $(DEMO)/dague-coeur.svg
	$(PY) $(SKILL)/scripts/buk_validate.py $(DEMO)/dague-coeur.svg
	$(PY) $(SKILL)/scripts/buk_stencil.py $(DEMO)/dague-coeur.svg --by both --out $(DEMO)/calques

buk-classiques:
	$(PY) research/design/flash_cc0.py

buk-motifs:
	$(PY) $(SKILL)/assets/composants/_generer_exemples.py

buk-package:
	rm -rf dist && mkdir -p dist
	cd skills && zip -rq ../dist/buk.zip buk -x '*/__pycache__/*' '*.pyc' '*/.DS_Store'
	@echo "dist/buk.zip prêt"

buk-research-list:
	$(PY) research/scripts/harvest.py list

buk-research-fetch:
	$(PY) research/scripts/harvest.py fetch -n 5

buk-coverage:
	$(PY) research/scripts/coverage.py

buk-clean:
	rm -rf dist
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
