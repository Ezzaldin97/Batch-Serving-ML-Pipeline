
install:
	poetry install

linting:
	bash scripts/linting.sh

train:
	poetry run dvc repro

run-pred-flow:
	poetry run python pred_flow.py