# Property Management System (PMS)

## Tech Stack
- Python 3.12+
- Django 5.x
- Django REST Framework 3.15+
- PostgreSQL
- Celery + Redis
- uv (dependency management)
- drf-spectacular (OpenAPI/Swagger)

## Project Structure
- `app/` Django project
- `app/api/` API apps (authentication, organization, maintenance)
- `start_api.sh` local/Docker entrypoint
- `docker-compose.yml` local dev stack

## Architecture (Brief)
- Modular Django REST API split by domain (`authentication`, `organization`, `maintenance`). 
- The system is multi-tenant using `organization_id` on tenant-aware models, enforced by view mixins and permission rules. 
- JWT provides stateless auth; Redis + Celery power async tasks. PostgreSQL is the primary datastore.

Simple process flow:
```
Client
  |  login -> JWT
  v
API (DRF + JWT)
  |  auth + org/permission checks
  v
PostgreSQL (tenant-scoped data)
  |
  +--> Celery (async tasks) -> Redis (broker/results)
```

The reasn for using uv, is for faster dependency resolution, reproducible installs via `uv.lock`, and consistent local/Docker workflows. It’s simpler and faster than pip/pipenv for this project, with minimal configuration and in the future good performance on CI/builds.

Trade-offs: 
- I prioritize a simple, monolithic Django app for faster iteration over microservice separation. 
- Tenant scoping is enforced in view logic (flexible but requires good test coverage). 
- Celery adds operational complexity but keeps request/response latency low for background work.
- The user registation and organization assignment to the users and not fully feleged and missses some critial edgecase which can result to bad user experience. This setup serves the current purpose but can be extended later

## Local Setup
- `git clone https://github.com/Georgeygigz/pms.git`
- `cd pms`
- `uv sync --frozen`
- `cp .env-sample .env` -> Update `.env` with your database and secret values.
- `uv run python manage.py makemigrations` &&  `uv run python manage.py migrate`
- `make server`

## Docker Setup
- `docker compose up --build`

## Swagger / OpenAPI
- Swagger UI: `http://127.0.0.1:8000/api/docs/`


## Authentication (JWT)
1) Call `POST /api/users/login/` in Swagger UI.
2) Copy the `token` from the response.
3) Click **Authorize** and paste: `Bearer <token>`

## Running Tests
```bash
uv run pytest --cov=app --cov-report=term-missing 

using make
make tests
```
