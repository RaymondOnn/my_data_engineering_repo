SHELL := /bin/bash # Tell Make this file is written with Bash as shell
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c # Bash strict mode
.DELETE_ON_ERROR:   # if a Make rule fails, it’s target file is deleted
#.DEFAULT_GOAL := all
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


REPO_NAME=$(notdir $(shell pwd))
PRODUCER_DIR = './src/web2kafka'
AIRFLOW_DIR = '../../tools/airflow_dev_env'
SPARK_DIR = ''

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start-producer-docker:
	docker compose -f $(PRODUCER_DIR)/docker-compose.yaml up -d

start-airflow:
	docker compose -f $(AIRFLOW_DIR)/docker-compose.yaml up -d

start-docker-all:
	make start-docker-produce

start-producer:
	pdm run python src/web2kafka/main.py

stop-producer-docker:
	docker compose -f $(PRODUCER_DIR)/docker-compose.yaml down

stop-airflow:
	docker compose -f $(AIRFLOW_DIR)/docker-compose.yaml down
