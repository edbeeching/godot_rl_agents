.PHONY: quality style test unity-test

# Switch between the download scripts based on OS
ifeq ($(OS),Windows_NT)
    SCRIPT = scripts\\get_all_examples_from_hub.bat
else
    SCRIPT = bash scripts/get_all_examples_from_hub.sh
endif

# Format source code automatically
style:
	black --line-length 120 --target-version py310 tests godot_rl examples
	isort -w 120 tests godot_rl examples
# Check that source code meets quality standards
quality:
	black --check --line-length 120 --target-version py310 tests godot_rl examples
	isort -w 120 --check-only tests godot_rl examples
	flake8 --max-line-length 120 tests godot_rl examples

# Run tests for the library
test:
	python -m pytest tests/

download_examples:
	@echo "Running script: $(SCRIPT)"
	$(SCRIPT)

wheel:
	rm dist/*
	python3 -m pip install --upgrade build
	python3 -m build

	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*