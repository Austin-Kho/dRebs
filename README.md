## Django + Nginx + MariaDB in docker

### Requirement

- docker
- docker-compose
  
- django & etc library
- nginx & uwsgi
- mariadb & mysqlclient

Static files Build and run :

```bash
cp docker-compose.tmpl.yml docker-compose.yml
```
write environments in docker-compose.yml
- required: 
  - MYSQL_DATABASE
  - MYSQL_ROOT_PASSWORD
  - MYSQL_USER
  - MYSQL_PASSWORD
  - DATABASE_NAME 
  - DATABASE_USER
  - DATABASE_PASSWORD
  - DJANGO_SETTINGS_MODULE
  - SERVER_NAME
  
```bash
docker-compose up -d --build
docker-compose exec web python manage.py collectstatic
```

### Usage

Migrations & Migrate settings

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

Create Superuser => your username & email & password settings

```bash
docker-compose exec web python manage.py createsuperuser
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

