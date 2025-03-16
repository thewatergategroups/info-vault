REPOSITORY := dune
SHELL := /bin/bash

build:
	docker build --network=host \
	-f ./Dockerfile \
	--target production \
	-t ghcr.io/thewatergategroups/$(REPOSITORY):latest \
	. 

up: 
	docker compose -f docker-compose.yml -f docker-compose.service.yml up -d --remove-orphans
	docker compose -f docker-compose.yml -f docker-compose.service.yml logs -f 

debug:
	docker run -it ghcr.io/thewatergategroups/$(REPOSITORY) bash

down: 
	docker compose -f docker-compose.yml -f docker-compose.service.yml down

push: build
	docker push ghcr.io/thewatergategroups/$(REPOSITORY):latest

migrate:
	docker compose up -d --remove-orphans
	python -m alembic revision --autogenerate -m "$(m)"
	docker compose down