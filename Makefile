.PHONY: quality style test unity-test

check_dirs := tests godot_rl

# Format source code automatically
style:
	black --line-length 120 --target-version py310 tests godot_rl
	isort -w 120 tests godot_rl
# Check that source code meets quality standards
quality:
	black --check --line-length 120 --target-version py310 tests godot_rl
	isort -w 120 --check-only tests godot_rl
	flake8 --max-line-length 120 tests godot_rl

# Run tests for the library
test:
	python -m pytest tests/

download_examples:
	bash scripts/get_all_examples_from_hub.sh

wheel:
	rm dist/*
	python3 -m pip install --upgrade build
	python3 -m build

	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*