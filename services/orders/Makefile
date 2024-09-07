add-migration:
	@read -p "Enter migration message: " MESSAGE; \
	docker compose run --rm app /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini revision --autogenerate -m '$$MESSAGE'"

apply-migrations:
	docker compose run --rm app /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini upgrade head"

unit-tests:
	docker compose -f docker-compose-test.yaml run --rm tests /bin/bash -c \
	"python -m pytest \
	tests -s -vv --cov . \
	--cov-report=html:/app/reports/coverage \
	--cov-report=xml:/app/reports/coverage/coverage.xml \
	--alluredir /app/allure-results"

allure:
	docker compose -f docker-compose-test.yaml up -d allure


bdd-tests:
	docker compose -f docker-compose-test.yaml run --rm bdd


sonar-scan:
	docker compose -f docker-compose-sonar.yaml run --rm sonar-scanner
