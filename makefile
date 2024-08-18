apply-migrations-%-service:
	docker compose run --rm $*_service /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini upgrade head"

apply-inventory-migrations: apply-migrations-inventory-service
	echo "Applying inventory migrations"

apply-orders-migrations: apply-migrations-orders-service
	echo "Applying orders migrations"

apply-delivery-migrations: apply-migrations-delivery-service
	echo "Applying delivery migrations"