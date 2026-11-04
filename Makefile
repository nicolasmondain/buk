PY ?= python3
SKILL := skills/buk
DEMO := flashs/dague-coeur

.PHONY: help link motifs test demo package research-list research-fetch coverage clean

help:
	@echo "make link            relie le skill pour Claude Code (.claude/skills/buk)"
	@echo "make test            tests de bout en bout"
	@echo "make demo            régénère le flash d'exemple et ses calques"
	@echo "make motifs          régénère les pièces d'exemple et leurs planches"
	@echo "make package         dist/buk.zip à importer dans claude.ai (Skills)"
	@echo "make research-list   catalogue les vidéos (research/sources.yaml)"
	@echo "make research-fetch  transcrit un lot de 5 vidéos (s'arrête si couverture atteinte)"
	@echo "make coverage        état de la couverture de recherche"

link:
	mkdir -p .claude/skills && rm -f .claude/skills/buk && ln -sfn ../../skills/buk .claude/skills/buk
	@echo ".claude/skills/buk -> skills/buk"

test:
	$(PY) -m unittest discover -s tests -v

demo:
	$(PY) $(SKILL)/assets/flash/_generer_dague_coeur.py
	mkdir -p $(DEMO)
	cp $(SKILL)/assets/flash/dague_coeur.svg $(DEMO)/dague-coeur.svg
	$(PY) $(SKILL)/scripts/buk_validate.py $(DEMO)/dague-coeur.svg
	$(PY) $(SKILL)/scripts/buk_stencil.py $(DEMO)/dague-coeur.svg --by both --out $(DEMO)/calques


motifs:
	$(PY) $(SKILL)/assets/composants/_generer_exemples.py

package:
	rm -rf dist && mkdir -p dist
	cd skills && zip -rq ../dist/buk.zip buk -x '*/__pycache__/*' '*.pyc' '*/.DS_Store'
	@echo "dist/buk.zip prêt"

research-list:
	$(PY) research/scripts/harvest.py list

research-fetch:
	$(PY) research/scripts/harvest.py fetch -n 5

coverage:
	$(PY) research/scripts/coverage.py

clean:
	rm -rf dist **/__pycache__
