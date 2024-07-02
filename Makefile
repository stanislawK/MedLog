COMPOSE_DEV=docker-compose -f docker-compose.yml

lint-local:
	ruff check --fix
lint:
	$(COMPOSE_DEV) run --rm --no-deps medlog bash -c ruff check --fix
format-local:
	ruff check --select I --fix && ruff format
format:
	$(COMPOSE_DEV) run --rm --no-deps medlog bash -c ruff check --select I --fix && ruff format
bash:
	$(COMPOSE_DEV) exec medlog bash
psql:
	$(COMPOSE_DEV) exec postgres psql -U postgres
