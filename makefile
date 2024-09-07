DOCKER_USERNAME := dmenezesgabriel
SERVICES := inventory orders payments delivery
SERVICES_WITH_MIGRATIONS := inventory orders delivery

.PHONY: apply-migrations-% apply-%-migrations apply-all-migrations run-% run-infra run-services show-logs-% show-services-logs build-% push-% buildall pushall clean

apply-migrations-%:
	docker compose run --rm $* /bin/bash -c \
	"alembic -c migrations/alembic/alembic.ini upgrade head"

apply-%-migrations: apply-migrations-%
	@echo "Applying $* migrations"

apply-migrations-all: $(addprefix apply-,$(addsuffix -migrations,$(SERVICES_WITH_MIGRATIONS)))
	@echo "All migrations applied"

run-%:
	docker compose up -d $*

wait-for-postgres:
	@until docker compose exec postgres pg_isready -U postgres; do \
		echo "Waiting for postgres..."; \
		sleep 2; \
	done

run-infra: run-rabbitmq run-postgres run-mongo wait-for-postgres apply-migrations-all
	@echo "Infrastructure is up and running"

run-services: $(addprefix run-,$(SERVICES))
	@echo "All services are running"

show-logs-%:
	docker compose logs --tail=100 -f $*

show-services-logs:
	@for service in $(SERVICES); do \
		docker compose logs --tail=100 $$service & \
	done; \
	wait

build-%:
	docker build -t $(DOCKER_USERNAME)/$*:latest ./$*

push-%:
	docker push $(DOCKER_USERNAME)/$*:latest

buildall: $(addprefix build-,$(SERVICES))
	@echo "All services built"

pushall: $(addprefix push-,$(SERVICES))
	@echo "All services pushed"

clean:
	docker compose down -v
	docker system prune -f

help:
	@echo "Available targets:"
	@echo "  apply-all-migrations   - Apply migrations for all services except payments"
	@echo "  run-infra              - Run infrastructure services"
	@echo "  run-services           - Run all application services"
	@echo "  show-services-logs     - Show logs for all services"
	@echo "  buildall               - Build Docker images for all services"
	@echo "  pushall                - Push Docker images for all services"
	@echo "  clean                  - Remove containers and prune Docker system"
	@echo "  help                   - Show this help message"
