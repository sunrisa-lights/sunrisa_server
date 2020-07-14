.PHONY: lint virtual test_unit test_integration mypy install install_integration run


lint:
	venv/Scripts/black sunrisa.py


test_unit:
	tests/integration/venv/Scripts/pytest -xv tests/


test_integration:
	tests/integration/venv/Scripts/pytest tests/integration/sunrisa_integration.py


mypy:
	venv/Scripts/mypy app/ ;\


install:
	python -m venv venv; \
	source venv/Scripts/activate; \
	pip install --upgrade -r requirements.txt; \



install_integration:
	python -m venv tests/integration/venv; \
	source tests/integration/venv/Scripts/activate; \
	pip install --upgrade -r tests/integration/requirements_integration.txt; \


run:
	venv/Scripts/python sunrisa.py
