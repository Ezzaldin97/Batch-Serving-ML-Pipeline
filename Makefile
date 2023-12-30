
install:
	poetry install

linting:
	bash scripts/linting.sh

train:
	poetry run dvc repro

run-data-flow:
	poetry run python data_flow.py