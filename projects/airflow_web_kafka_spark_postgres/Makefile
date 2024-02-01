SHELL := /bin/bash # Tell Make this file is written with Bash as shell
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c # Bash strict mode
.DELETE_ON_ERROR:   # if a Make rule fails, it’s target file is deleted
#.DEFAULT_GOAL := all
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

WORKDIR = $(shell pwd)
VENV = .venv
VENV_DIR=$(WORKDIR)/${VENV}
VENV_BIN=$(VENV_DIR)/bin
PYTHON=${VENV_BIN}/python3
PIP=$(VENV)/bin/pip
SPARK_FLDR=kafka2postgres
KAFKA_DIR=$(WORKDIR)/web2kafka
SPARK_DIR=$(WORKDIR)/$(SPARK_FLDR)
SPARK_CONTAINER=da-spark-master

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check:
	dirname $(SPARK_DIR)


$(ENV)/bin/activate: requirements.txt ## creating virtual environment
	python3 -m venv $(ENV) \
		&& chmod +x $(VENV)/bin/activate \
		&& . ./$(VENV)/bin/activate \
		&& $(PIP) install -r requirements.txt

#venv: $(VENV)/bin/activate  ## activate virtual environment
#    . ./$(VENV)/bin/activate
#
#run: venv ## run python file
#    $(PYTHON) app.py
#

venv-update: requirements.txt
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	rm -rf __pycache__ *.pyc .pytest_cache;

.PHONY: clean-all
clean-all:
	rm -rf __pycache__ *.pyc .pytest_cache;
	rm -rf $(VENV)

.PHONY: kafka-task-img
kafka-task-img:
	docker build -f $(KAFKA_DIR)/airflow/task.Dockerfile -t task_web2kafka .

.PHONY: airflow-start
airflow-start:
	docker compose -f ./airflow/docker-compose.yaml up -d

.PHONY: airflow-stop
airflow-stop:
	docker compose -f ./airflow/docker-compose.yaml down

.PHONY: spark-bash
spark-bash:
	docker container exec -it $(SPARK_CONTAINER) /bin/bash

.PHONY: spark-start
spark-start:
	docker compose -f $(SPARK_DIR)/docker-compose.yaml up -d

.PHONY: spark-stop
spark-stop:
	docker compose -f $(SPARK_DIR)/docker-compose.yaml down

.PHONY: spark-pex
spark-pex: $(shell find $(SPARK_DIR)/src -type f)
	docker container run --rm -v $(SPARK_DIR):/build pex-tool \
		pex --python=python3 \
			--inherit-path=prefer \
			-r ./requirements.txt  \
			-o ./airflow/job.pex \
			-D ./src

.PHONY: spark-img
spark-img:
	docker compose build -f $(SPARK_DIR)/docker-compose.yaml

