SHELL  := /bin/bash

### Server

docker-build:
	docker stop $$(docker ps -aq)
	docker-compose -f local.yml build
	#docker-compose -f local.yml build --force-rm --no-cache

docker-up:
	docker stop $$(docker ps -aq)
	docker-compose -f local.yml up -d

docker-up-django:
	docker-compose -f local.yml up -d django

docker-up-postgres:
	docker-compose -f local.yml up -d postgres

docker-down:
	docker-compose -f local.yml down

### extra commands

docker-bash:
	docker-compose -f local.yml run --rm django /bin/bash

docker-shell:
	docker-compose -f local.yml run --rm django python manage.py shell

docker-test:
	docker-compose -f local.yml run --rm django python manage.py test

docker-compilemessages:
	docker-compose -f local.yml run --rm django python manage.py compilemessages

docker-createsuperuser:
	docker-compose -f local.yml run --rm django python manage.py createsuperuser

docker-makemessages:
	docker-compose -f local.yml run --rm django python manage.py makemessages -a

docker-makemigrations:
	docker-compose -f local.yml run --rm django python manage.py makemigrations

docker-migrate:
	docker-compose -f local.yml run --rm django python manage.py migrate


### Logs
docker-django-logs:
	docker logs scoringengine_local_django --follow --since 30s


### Format files

format-all-files:
	for f in `find ./ -iname *.py -print`; do echo "Formatting $$f"; black -t py310 "$$f" >/dev/null 2>&1 ; done

format-changed-files:
	for f in `git status --porcelain | grep '\.py$$' | awk '{ print $$2 }'`; do if [ -f "$$f" ]; then echo "Formatting $$f"; black -t py310 "$$f" >/dev/null 2>&1; fi;  done



### Locally executed scripts

createsuperuser:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py createsuperuser

makemigrations:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py makemigrations

makemigrations-merge:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py makemigrations --merge

migrate:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py migrate

shell:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py shell

test:
	export DJANGO_READ_DOT_ENV_FILE=True && python manage.py test
