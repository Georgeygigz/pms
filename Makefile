shell:
	uv run manage.py shell
migrations:
	uv run manage.py makemigrations
migrate:
	uv run manage.py migrate
superuser:
	uv run manage.py createsuperuser
collectstatic:
	uv run manage.py collectstatic
check:
	uv run manage.py check
server:
	uv run manage.py runserver
tests:
	uv run pytest --cov=app --cov-report=term-missing
