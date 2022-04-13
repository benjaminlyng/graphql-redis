# Graphql-redis
Example application meant to show (and learn) how to setup a graphql api using the python framework strawberry. Redis is used as a storage backend in stead of a traditional database because reasons.

## Buzzwords:
* Graphql [Strawberry](https://strawberry.rocks/)
* FastAPI
* Pydantic
* Redis

## Quickstart:
Start redis in docker: \
```docker run -p 6379:6379 -d redislabs/redis:latest```

Install dependencies with `poetry install` and run the application:\
`poetry run uvicorn graphql_redis.schema:app --reload`

Now the application should be available at http://127.0.0.1:8000/graphql

## Data model:
The data model is inspired by the excellent documentation at https://strawberry.rocks. It consists of "books" and "Authors". Books have an id, a title and an while authors have an id, a name and a list of books that they have authored. To store this data in redis we use hashes with namespaces like "Book:\<id>". The key "Book:1" then contains information about the book with id=1. The same for authors, using "Author:\<id>"

To lookup the list of books written by an author a set is used in redis, again using a namespace "BooksByAuthor:\<id>". When a new book is created its id is added to the set. To query the books written by a specific author just use each id from the set to lookup data on the books.

## TODOs:
* Make mypy happy (as if...)
* Add tests
