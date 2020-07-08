.PHONY: lint virtual
all: lint virtual

lint:
	venv/Scripts/black sunrisa.py

virtual:
	python -m venv venv; \
	source venv/Scripts/activate; \
	pip install --upgrade -r requirements.txt; \
	mypy app; \


