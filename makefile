apply-migrations-delivery-service:
	docker compose run --rm delivery_service /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini upgrade head"
