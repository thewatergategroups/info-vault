REPOSITORY := dp
SHELL := /bin/bash

build:
	docker build --network=host \
	-f ./Dockerfile \
	--target production \
	-t ghcr.io/1ndistinct/$(REPOSITORY):latest \
	. 

up: 
	docker compose up -d --remove-orphans
	docker compose logs -f 

debug:
	docker compose run -it $(REPOSITORY) bash

down: 
	docker compose --profile "*" down

push: build
	docker push ghcr.io/1ndistinct/$(REPOSITORY):latest

test: 
	docker run --rm -p 5431:5432 --name test-db --env POSTGRES_USER=postgres --env POSTGRES_DB=postgres --env POSTGRES_PASSWORD=postgres -d postgres:16
	sleep 0.5
	pytest -vv  tests || :
	docker kill test-db

migrate:
	docker compose run --entrypoint "python -m alembic -c $(REPOSITORY)/database/alembic.ini revision --autogenerate -m '$(m)'" $(REPOSITORY)