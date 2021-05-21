# Scoring Engine

Customizable Scoring and Rules model

## Deployment

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)

### Local

#### Build the Stack

    docker-compose -f local.yml build

#### Run the Stack

    docker-compose -f local.yml up

#### Misc

    docker-compose -f local.yml run --rm django python manage.py makemigrations scoringengine
    docker-compose -f local.yml run --rm django python manage.py migrate

    docker-compose -f local.yml run --rm django python manage.py shell
