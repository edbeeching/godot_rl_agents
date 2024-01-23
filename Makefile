.PHONY: quality style test unity-test

check_dirs := src tests godot_rl

# Format source code automatically
style:
	python -m black --line-length 119 --target-version py310 $(check_dirs) setup.py
	python -m isort $(check_dirs) setup.py
# Check that source code meets quality standards
quality:
	python -m black --check --line-length 119 --target-version py310 $(check_dirs) setup.py
	python -m isort --check-only $(check_dirs) setup.py
	python -m flake8 --max-line-length 119 $(check_dirs) setup.py

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