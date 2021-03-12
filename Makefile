.PHONY: pre build-up up-d build-up-d logs curr-logs stop clean clean_volume lint virtual test_unit test_integration mypy install install_integration run test up message-protos protos

pre:
	pre-commit run --all-files

build-up:
	docker-compose up --build

up-d:
	docker-compose up -d

build-up-d:
	docker-compose up -d --build

logs:
	docker-compose logs -f -t

curr-logs:
	docker-compose logs -f -t --tail=1000

stop:
	docker-compose stop

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

message-protos:
	mkdir -p app/generated
	venv/bin/python -m grpc_tools.protoc --proto_path=app/protos --python_out=app/generated app/protos/job_scheduler.proto

protos:
	mkdir -p app/generated
	venv/bin/python -m grpc_tools.protoc -I=app/protos --python_out=app/generated --grpc_python_out=app/generated app/protos/job_scheduler.proto
