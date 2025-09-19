build-backend:
	docker compose --file ./docker-compose.yml up -d --build

start-backend:
	docker compose --file ./docker-compose.yml up -d

stop:
	docker compose --file ./docker-compose.yml stop

down:
	docker compose --file ./docker-compose.yml down