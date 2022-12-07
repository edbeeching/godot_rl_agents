.PHONY: quality style test unity-test

# Check that source code meets quality standards
quality:
	black --check --line-length 119 --target-version py38 tests godot_rl 
	isort --check-only tests godot_rl 
	flake8 tests godot_rl

# Format source code automatically
style:
	black --line-length 119 --target-version py38 tests godot_rl
	isort tests godot_rl

# Run tests for the library
test:
	python -m pytest tests/

wheel:
	rm dist/*
	python3 -m pip install --upgrade build
	python3 -m build

	python3 -m pip install --upgrade twine
	python3 -m twine upload --repository testpypi dist/*