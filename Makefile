.PHONY: quality style test unity-test

# Check that source code meets quality standards
quality:
	black --check --line-length 119 --target-version py38 tests godot_rl_agents 
	isort --check-only tests godot_rl_agents 
	flake8 tests godot_rl_agents

# Format source code automatically
style:
	black --line-length 119 --target-version py38 tests godot_rl_agents
	isort tests godot_rl_agents  

# Run tests for the library
test:
	python -m pytest tests/

