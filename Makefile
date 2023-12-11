
install:
	poetry install

linting:
	bash scripts/linting.sh

run-pred-flow:
	poetry run pred_flow.py