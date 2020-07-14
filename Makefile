.PHONY: lint virtual test_unit test_integration mypy install install_integration run

lint:
	venv/bin/black sunrisa.py


test_unit:
	tests/integration/venv/bin/pytest -xv tests/


test_integration:
	tests/integration/venv/bin/pytest tests/integration/sunrisa_integration.py


mypy:
	venv/bin/mypy app/ ;\


install:
	python -m venv venv; \
	source venv/bin/activate; \
	pip install --upgrade -r requirements.txt; \



install_integration:
	python -m venv tests/integration/venv; \
	source tests/integration/venv/bin/activate; \
	pip install --upgrade -r tests/integration/requirements_integration.txt; \


run:
	venv/bin/python sunrisa.py
