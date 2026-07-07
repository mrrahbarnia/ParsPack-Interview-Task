# ParsPack Interview Task

## Run the project

Start all services:

```bash
docker compose up --build
```

## Apply database migrations

In another terminal, run:

```bash
docker compose exec -it app sh -c "alembic upgrade head"
```

## Swagger Documentation

After the application is running, Swagger is available at:

```
http://localhost:8000/docs
```