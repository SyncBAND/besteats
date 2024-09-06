# Besteats

Besteats allows users to cast votes on restaurants.

Django 5 pre-configured with the following side-services and libraries:

* [Django Admin](https://docs.djangoproject.com/en/5.1/ref/contrib/admin/) configured with [Constance config](https://django-constance.readthedocs.io/en/latest/) which is where the admin can update the "configurable" daily user votes.
* [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) - Background task/job runner, along with the popular [django-celery-beat](https://github.com/celery/django-celery-beat) integration which allows us to configure cronjobs and schedule tasks in the admin interface e.g. that resets the users daily votes.
* [REST Framework](https://www.django-rest-framework.org/) - API endpoint development framework built on top of Django. Minimally configured so we can have endpoints to interact with frontend.
* [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/readme.html) - generates Swagger documentation for our REST Framework endpoints at `/api/swagger`.

This is all wrapped up into a `docker-compose` environment with development defaults. The only configuration required is a random `SECRET_KEY`. Postgres which waits for the service to be ready and Redis are all preconfigured.

We've configured docker-compose to run flake8 and tests using default values in the `example.env` file.



## Preconfigured project modules/features
A complete list of everything included in this app beyond what you get from the default Django cookiecutter.

### Django
* Application with the name `besteats` created
* `apps/` module created for our apps
* Cache enabled with Redis backend
* `settings.py` greatly expanded beyond the default options in the file.
* Admin page settings added for `staff` to investigate changes
* `constance.py` pattern implemented as an optional alternative to environment variables for configuration

### `utils` App
* Functions and classes that are reusable accross the project e.g. get or set constance config

### `resturants` App
* Users can `create` restaurants and `update or delete` restaurants they have added.
* Users can set a`vote or unvote` restaurants. 
* Each user is given a `daily vote limit` which resets at midnight. 
* User's cast the first vote towards a particular restaurant which amounts to 1 point, second amounts to 0.5 and the rest amount to 0.25 points.


### REST Framework
* Integrated into Django
* Standard base config defined in `settings.py`
* Swagger documentation generation configured at `/api/swagger`
* Documentation toggled on and off with `ENABLE_BROWSEABLE` setting

### Celery
* Integrated into project
* Django Beat scheduler added so you can configure scheduled tasks using the django admin interface
* Default configuration uses redis as broker and result backend

### Constance
* Accessible on Django Admin
* Config changes can be made while the app is running with no need of rebooting the server
* Update the `USER_DAILY_VOTES`


## Usage

### Setup

Please ensure you have Docker Compose installed. If not, you can get it [here](https://medium.com/@meghasharmaa704/installing-docker-compose-d6233d8bf3c3)

1. `cp example.env .env` in root folder
2. Update variables in `.env`
3. Run `docker-compose build`
4. Run migrations with `docker-compose run --rm backend ./manage.py migrate`
5. Create a superuser with `docker-compose run --rm backend ./manage.py createsuperuser`
6. Update `Constance Config` values on Django Admin

### Running

`docker-compose up` to start the project

* [http://localhost:8000/api/swagger](http://localhost:8000/api/swagger) to access the swagger
* [http://localhost:8000/admin](http://localhost:8000/admin) to access the admin

1. We'll be using Postman because we're able to update `environment variables` using scripts
2. Import the `besteats.postman_collection.json` and `besteats.postman_environment.json` files found in the root folder. See [here](https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data/) or [here](https://apidog.com/articles/how-to-import-json-files-into-postman/) for guidance on how to import the files.
3. Navigate to `Besteats/authentication/registration` and register at least 3 users using the `http://{{base_url}}/api/auth/registration/` endpoint
4. Navigate to `Besteats/restaurants/create`, update the `Body` and create at least 3 restaurants.
5. Now we can cast votes on the latest created restaurant i.e. `{restaurant_id}`, using `Besteats/restaurants/vote`
6. We can cast votes on other restaurants by changing the `{restaurant_id}` env variable or updating the URL - `http://{{base_url}}/api/restaurants/{{restaurant_id}}/vote`. Use the `Besteats/restaurants/list` to get the restaurant IDs.
7. Users can unvote from restaurants using `Besteats/restaurants/unvote`
8. Users can also view the restaurant or restaurants with the most votes today using `Besteats/restaurants/most_voted`
9. To view the previos winner(s) on a specific date, update the `query params` using `date` as the key and the value should be in the following format `YYYY-MM-DD`, e.g. `http://{{base_url}}/api/restaurants/most_voted?date=2024-07-10`
10. Login as a different user using `Besteats/authentication/login` to cast more votes
11. To reset the daily user votes, we can use the managemnent command `docker-compose run --rm backend ./manage.py reset_daily_votes_for_all_profles` or wait until the next day.
12. Try replicate the scenario in the tests `test_most_voted_restaurant` and `test_most_voted_restaurants` both found in `besteats/apps/restaurants/tests/integration/test_restaurant_views`
13. Note: only users who created a restaurant and staff can make updates to it.


### Operations

These operations assume the project is already up and are to be run in a second terminal session.

* **Flake8**: `docker-compose exec backend flake8`
* **Generate migrations**: `docker-compose exec backend ./manage.py makemigrations`
* **Run migrations**: `docker-compose exec backend ./manage.py migrate`
* **Create superuser**: `docker-compose exec backend ./manage.py createsuperuser`
* **Create a new app**: `docker-compose exec backend ./manage.py startapp <APP_NAME>` (and drag it into the `apps/` folder)
* **Run the project in the background**: `docker-compose up -d`
* **Run tests with coverage**: `docker-compose exec backend sh -c "coverage run --source='.' ./manage.py test && coverage report -m --omit=*/tests/*,*/migrations/*,*manage.py,*wsgi.py,*asgi.py"`

### Teardown

* **Completely stop the project**: `docker-compose down`
* **Delete the project and delete database/S3 data**: `docker-compose down -v`
