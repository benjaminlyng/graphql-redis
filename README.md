# Graphql-redis
Example application meant to show (and learn) how to setup a graphql api using the python framework strawberry. Redis is used as a storage backend in stead of a traditional database because reasons.

## Quickstart:
Start redis in docker: \
```docker run -p 6379:6379 -d redislabs/redis:latest```

Install dependencies with `poetry install` and run the application:\
`poetry run uvicorn graphql_redis.schema:app --reload`

Now the application should be available at http://127.0.0.1:8000/graphql

## Buzzwords:
* Graphql [Strawberry](https://strawberry.rocks/)
* FastAPI
* Pydantic
* Redis

## TODOs:
* Make mypy happy (as if...)
* Add tests
