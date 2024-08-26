apply-migrations-%-service:
	docker compose run --rm $*_service /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini upgrade head"

apply-inventory-migrations: apply-migrations-inventory-service
	echo "Applying inventory migrations"

apply-orders-migrations: apply-migrations-orders-service
	echo "Applying orders migrations"

apply-delivery-migrations: apply-migrations-delivery-service
	echo "Applying delivery migrations"

apply-all-migrations: apply-inventory-migrations apply-orders-migrations apply-delivery-migrations
	echo "Applying all migrations"

run-%:
	docker compose up -d $*

run-infra: run-rabbitmq run-postgres run-mongo apply-all-migrations
	echo "Running infra"

run-services: run-inventory_service run-orders_service run-payments_service run-delivery_service
	echo "Running services"

show-logs-%:
	docker compose logs $*

show-services-logs: show-logs-inventory_service show-logs-orders_service show-logs-payments_service show-logs-delivery_service
	echo "Show logs"