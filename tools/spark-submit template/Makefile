SHELL := /bin/bash # Tell Make this file is written with Bash as shell
.ONESHELL: #  each Make recipe is ran as one single shell session
.SHELLFLAGS := -eu -o pipefail -c # Bash strict mode
.DELETE_ON_ERROR:   # if a Make rule fails, it’s target file is deleted
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


VERSION=$(strip $(shell cat VERSION))
REPO_NAME=$(notdir $(shell pwd))
CONTAINER_NAME=da-spark-master
JOB_NAME = pi
WORKDIR=/opt/spark/workdir
PEX_FOLDER=dist


.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## build spark docker image
	docker-compose build

build-nc:
	docker-compose build --no-cache

build-progress:
	docker-compose build --no-cache --progress=plain

del:
	docker container rm $(CONTAINER_NAME)

start-spark: ## running docker containers
	docker compose -f docker-compose.yaml up -d	

start-spark-big: ## running docker containers with more workers
	docker compose -f docker-compose.yaml up --scale spark-worker=3

stop-spark: ## stop and remove running containers
	docker compose -f docker-compose.yaml down --volumes

refresh: ## stop and remove running containers, before rebuilds and running new image
	make down && docker compose -f docker-compose.yaml up --build -d

spark-bash: ## open spark terminal on spark-master
	@docker exec -it $(CONTAINER_NAME) /bin/bash

pex:  ## package job dependencies into pex file
	rm -rf ./$(PEX_FOLDER); 
	docker exec $(CONTAINER_NAME) /bin/bash -c \
		'pex --python=python3 \
			--inherit-path=prefer \
			-r prod.txt \
			-o $(WORKDIR)/$(PEX_FOLDER)/jobs.pex \
			-D $(WORKDIR)'

submit: pex ## submit job for execution
	docker exec $(CONTAINER_NAME) /bin/bash -c \
		'spark-submit \
			--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0,org.apache.spark:spark-avro_2.12:3.5.0 \
			--conf spark.pyspark.python=$(WORKDIR)/$(PEX_FOLDER)/jobs.pex \
				$(WORKDIR)/entrypoint.py --job nrt'

exec-submit:  $(shell find $$(WORKDIR)/jobs -type f)   ## (for test job) package job dependencies into pex file
		rm -rf ./app/$(PEX_FOLDER);
		docker exec $(CONTAINER_NAME) /bin/bash -c \
			'pex --python=python3 \
				--inherit-path=prefer \
				-r $(WORKDIR)/jobs/$(JOB_NAME)/requirements.txt \
				-o $(WORKDIR)/$(PEX_FOLDER)/jobs.pex \
				-D $(WORKDIR)/jobs'

# --env-var partitions=4 --env-var sample_size=20000000'
test-submit: $(WORKDIR)/$(PEX_FOLDER)/jobs.pex ## (for test job) submit job for execution
	docker exec $(CONTAINER_NAME) /bin/bash -c \
		'spark-submit \
		--master spark://spark-master:7077 --deploy-mode client \
		--conf spark.pyspark.python=$(WORKDIR)/$(PEX_FOLDER)/jobs.pex \
			$(WORKDIR)/jobs/entrypoint.py --job $(JOB_NAME) --job-arg date=2021-12-12'

test-exec: test-submit

submit_draft:
	docker exec da-spark-master spark-submit --master spark://spark-master:7077 --deploy-mode client ./apps/$(app)


test: 
	@echo \
		"rm -rf $(PEX_FOLDER); \
		docker exec $(CONTAINER_NAME) /bin/bash -c \
			pex --python=python3 --inherit-path=prefer \
			-r test.txt -o $(PEX_FOLDER)/jobs.pex -D $(WORKDIR)"

unittest:
	@docker exec -it $(CONTAINER_NAME) /bin/bash -c \
		"python3 -m pytest -s --disable-warnings $(WORKDIR)/tests/"

