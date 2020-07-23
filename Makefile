.PHONY: build-up clean clean_volume lint virtual test_unit test_integration mypy install install_integration run test up

build-up: 
	docker-compose up --build


clean:
	docker system prune -f\


clean_volume:
	docker volume prune -f


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


test:
	docker-compose -f docker-compose.test.yml up


up: 
	docker-compose up








