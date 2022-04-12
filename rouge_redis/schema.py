import typing

import redis
import strawberry
from fastapi import Depends
from fastapi import FastAPI
from more_itertools import first
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info


def get_redis():
    yield redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def get_context(redis=Depends(get_redis)):
    return {"redis": redis}


@strawberry.type
class Book:
    title: str
    author: str


def get_book(id: strawberry.ID, info: Info):
    r: redis.Redis = info.context["redis"]
    name = f"Book::{id}"
    book = r.hgetall(name)
    if not book:
        raise ValueError("No book found")
    return Book(**book)


def get_books(info: Info):
    r: redis.Redis = info.context["redis"]
    # TODO: once redisgears-py is compatible with redis 4 use that
    books = first(r.execute_command("RG.PYEXECUTE GearsBuilder().run('Book:*')"))
    # TODO: Don't use eval
    books = list(map(eval, books))
    if not books:
        raise ValueError("No books found")
    return [Book(**book.get("value")) for book in books]


@strawberry.type
class Query:
    books: typing.List[Book] = strawberry.field(resolver=get_books)
    book: Book = strawberry.field(resolver=get_book)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, id: strawberry.ID, title: str, author: str, info: Info) -> Book:
        r: redis.Redis = info.context["redis"]
        name = f"Book::{id}"
        r.hset(name, mapping={"author": author, "title": title})
        return Book(title=title, author=author)


schema = strawberry.Schema(Query, Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
