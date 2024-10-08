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
watch-fe:
	npx tailwindcss -i ./medlog/static/src/input.css -o ./medlog/static/src/output.css --watch
messages:
	cd ./medlog && django-admin makemessages -l pl
compile-messages:
	cd ./medlog && django-admin compilemessages
pip-compile-local:
	uv pip compile requirements.in -o requirements.txt
pip-sync-local:
	uv pip sync requirements.txt
