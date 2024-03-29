
install:
	poetry install

linting:
	bash scripts/linting.sh

train:
	poetry run dvc repro

run-data-flow:
	poetry run python data_flow.py

run-pred-flow:
	poetry run python pred_flow.py

run-monitor-flow:
	poetry run python monitor_flow.py