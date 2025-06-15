# HOLY REMIX Makefile

# Configuration
PYTHON = python3
PIP = pip3
AWS_CLI = aws

# Default target
.PHONY: help
help:
	@echo "🎭 HOLY REMIX - AI-Powered Scripture Reimagined"
	@echo ""
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make preprocess       - Preprocess Bible data"
	@echo "  make list-personas    - List available personas"
	@echo "  make estimate-full-bible PERSONA=<name> - Estimate translation cost"
	@echo "  make translate-full-bible PERSONA=<name> - Translate entire Bible"
	@echo "  make translate-chapter BOOK=<name> CHAPTER=<num> PERSONA=<name> - Translate single chapter"
	@echo "  make test-translation PERSONA=<name> - Test translation with sample"
	@echo "  make clean            - Clean up generated files"
	@echo "  make help             - Show this help message"

PYTHON=python3
VENV=venv
PYTHON_VENV=$(VENV)/bin/python
PIP_VENV=$(VENV)/bin/pip
BOOK?=Genesis
CHAPTER?=1
KJV_FILE=data/processed/kjv_bible.json

.PHONY: help venv install preprocess test list-personas estimate-full-bible translate-full-bible translate-chapter clean test-translation run-tests standard-bible

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created. Run 'source venv/bin/activate' to activate."

install: venv
standard-bible:
	@echo "📥 Downloading standard BBE.json Bible file..."
	@mkdir -p data/input
	@curl -L -o data/input/BBE.json https://raw.githubusercontent.com/scrollmapper/bible_databases/refs/heads/master/formats/json/BBE.json
	@echo "✅ BBE.json downloaded to data/input/BBE.json"
	@echo "📊 File size: $$(du -h data/input/BBE.json | cut -f1)"
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	@echo "✅ Dependencies installed in virtual environment."

preprocess: install
	@if [ -f "data/input/BBE.json" ]; then \
		echo "📖 Processing BBE.json..."; \
		$(PYTHON_VENV) scripts/preprocess_bible.py data/input/BBE.json --output data/processed/kjv_bible.json; \
	elif [ -f "data/input/kjv.json" ]; then \
		echo "📖 Processing kjv.json..."; \
		$(PYTHON_VENV) scripts/preprocess_bible.py data/input/kjv.json --output data/processed/kjv_bible.json; \
	else \
		echo "📖 No input files found, using sample data..."; \
		$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from preprocessors.json_preprocessor import main; main()"; \
	fi

test: install
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from utils.test_setup import main; main()"

run-tests: install
	@echo "🧪 Running all tests..."
	@for test_file in tests/test_*.py; do \
		echo "Running $$test_file..."; \
		$(PYTHON_VENV) $$test_file || exit 1; \
	done
	@echo "✅ All tests completed successfully!"

list-personas: install
	$(PYTHON_VENV) scripts/translate_bible.py --list-personas

estimate-full-bible: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make estimate-full-bible PERSONA=joe-rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from translators.full_bible_translator import FullBibleTranslator; translator = FullBibleTranslator('$(PERSONA)'); translator.estimate_cost()"

translate-full-bible: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make translate-full-bible PERSONA=joe-rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from translators.full_bible_translator import FullBibleTranslator; translator = FullBibleTranslator('$(PERSONA)'); translator.translate_full_bible()"

translate-chapter: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make translate-chapter PERSONA=joe-rogan BOOK=Genesis CHAPTER=1"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from translators.chapter_translator import ChapterTranslator; translator = ChapterTranslator('$(PERSONA)'); translator.translate_chapter('$(BOOK)', $(CHAPTER))"

test-translation: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make test-translation PERSONA=joe-rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); import json; from translators.chapter_translator import ChapterTranslator; bible_data = json.load(open('data/processed/kjv_bible.json')); verses = bible_data['Genesis']['1']; translator = ChapterTranslator(); result = translator.translate_chapter('Genesis', '1', verses, '$(PERSONA)'); print('Translation result:', result)"

# Legacy commands (deprecated but kept for backward compatibility)
quote: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make quote PERSONA=joe_rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, 'src/holyremix'); from utils.quote_generator import main; import sys; sys.argv = ['quote_generator.py', '--persona', '$(PERSONA)']; main()"

translate: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make translate PERSONA=joe_rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) scripts/translate_bible.py --persona $(PERSONA)

dry-run: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make dry-run PERSONA=cardi_b"; \
		exit 1; \
	fi
	$(PYTHON_VENV) scripts/translate_bible.py --persona $(PERSONA) --dry-run

chapter: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make chapter PERSONA=maya_angelou BOOK=John CHAPTER=1"; \
		exit 1; \
	fi
	$(PYTHON_VENV) scripts/translate_bible.py --persona $(PERSONA) --book $(BOOK) --chapter $(CHAPTER)

chapter-estimate: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make chapter-estimate PERSONA=joe_rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) scripts/translate_bible_chapters.py --persona $(PERSONA) --estimate-only

chapter-translate: install
	@if [ -z "$(PERSONA)" ]; then \
		echo "Error: PERSONA is required. Usage: make chapter-translate PERSONA=joe_rogan"; \
		exit 1; \
	fi
	$(PYTHON_VENV) scripts/translate_bible_chapters.py --persona $(PERSONA) --checkpoint checkpoint_$(PERSONA).json

clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf data/processed/*
	rm -f checkpoint_*.json
	rm -f translated_bible_*.json
	rm -rf logs/*
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/*/__pycache__
	rm -rf scripts/__pycache__
	rm -rf tests/__pycache__
	@echo "✅ Cleanup complete!" 
