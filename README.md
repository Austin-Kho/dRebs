## Django + Nginx + MariaDB in docker

### Requirement

- docker
- docker-compose

Static files Build and run :

```
docker-compose run web ./manage.py collectstatic
docker-compose up -d
```

### Usage

Migrations & Migrate settings

```
docker-compose run web ./manage.py makemigrations
docker-compose run web ./manage.py migrate
```

Create Superuser => your username & email & password settings

```
docker-compose run web ./manage.py createsuperuser
```

Data Seeding (After build to db & web)

```
docker-compose exec web python manage.py loaddata rebs/fixtures/seeds-data.json 
```


### Reference
- [Python](www.python.org)
- [Docker](www.docker.com)
    - [Docker compose](docs.docker.com/compose)
- [Django](www.djangoproject.com)
- [MariaDB](mariadb.org)
- [Nginx](https://www.nginx.com/)

