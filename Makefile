
install:
	poetry install

linting:
	bash scripts/linting.sh

run-pred-flow:
	poetry run python pred_flow.py