SHELL := /bin/bash # Tell Make this file is written with Bash as shell
# .ONESHELL: #  each Make recipe is ran as one single shell session
.SHELLFLAGS := -eu -o pipefail -c # Bash strict mode
.DELETE_ON_ERROR:   # if a Make rule fails, it’s target file is deleted
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

VENV = venv
VENV_DIR=$(shell pwd)/${VENV}
VENV_BIN=$(VENV_DIR)/bin
PYTHON=${VENV_BIN}/python3
PIP = $(VENV)/bin/pip


	
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# creating virtual environment
# $(VENV_BIN)/activate: requirements.txt
# 	test -d $(VENV_DIR) || python3 -m venv $(VENV) \
# 		&& ${PYTHON} -m pip install -r requirements.txt \
# 		&& chmod +x $(VENV_BIN)/activate

# venv: $(VENV_BIN)/activate
# 	. $(VENV_BIN)/activate 

venv: requirements.txt
	test -d $(VENV_DIR) || python3 -m venv $(VENV) \
		&& ${PYTHON} -m pip install -r requirements.txt \
		&& chmod +x $(VENV_BIN)/activate;
		source $(VENV)/bin/activate 

venv-update: requirements.txt
	$(PIP) install -r requirements.txt

run: ./app.py
	flask run

dev-run: ./app.py
	flask run --reload

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

clean-all:
	rm -rf __pycache__ *.pyc .pytest_cache; 
	rm -rf $(VENV)

img: requirements.txt Dockerfile
	docker build -t flask-smorest-api .

start: 
	docker run -p 5000:5000 -w /app -v ./:/app flask-smorest-api


# 1. creates ./migrations folder. Errors if flask run fails
# 2. Create migration file
# 3. Create data.db file OR database tables
init-migrate: app.py
	flask db init

update-migrate: ./migrations
	flask db migrate && flask db upgrade

debug:
	echo $(VENV_BIN)