## Django + Nginx + MariaDB in docker

### Requirement in your system

- docker
- docker-compose

### Usage

###### Copy docker-compose.yml
```bash
cp docker-compose.tmpl.yml docker-compose.yml
```

###### Write environments in docker-compose.yml
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
  
###### Build and run
```bash
docker-compose up -d --build
```

###### Migrations & Migrate settings (After build to db & web)

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

###### Create Superuser => your username & email & password settings

```bash
docker-compose exec web python manage.py createsuperuser
```

###### Data Seeding

```
docker-compose exec web python manage.py loaddata rebs/fixtures/seeds-data.json 
```

※ Place your Django project in the **src** directory and develop it.


### Reference
- [Python](www.python.org)
- [Docker](www.docker.com)
    - [Docker compose](docs.docker.com/compose)
- [Django](www.djangoproject.com)
- [MariaDB](mariadb.org)
- [Nginx](https://www.nginx.com/)

