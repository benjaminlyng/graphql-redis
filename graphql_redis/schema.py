from typing import List

import redis
import strawberry
from fastapi import Depends
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info


def get_redis():
    yield redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def get_context(redis=Depends(get_redis)):
    return {"redis": redis}


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    author: "Author"


def get_books_by_author(root: "Author", info: Info) -> List["Book"]:
    r: redis.Redis = info.context["redis"]
    book_ids = r.smembers(f"BooksByAuthor:{root.id}")
    books = {b: r.hgetall(f"Book:{b}") for b in book_ids}
    res = [Book(id=i, title=b["title"], author=root) for i, b in books.items()]
    return res


@strawberry.type
class Author:
    id: strawberry.ID
    name: str
    books: List[Book] = strawberry.field(resolver=get_books_by_author)


def get_book(id: strawberry.ID, info: Info):
    r: redis.Redis = info.context["redis"]
    name = f"Book:{id}"
    book = r.hgetall(name)
    if not book:
        raise ValueError("No book found")
    author = r.hgetall(f"Author:{book['author']}")
    return Book(id=id, title=book["title"], author=Author(**author))


def get_books(info: Info):
    r: redis.Redis = info.context["redis"]
    books = r.scan_iter(match="Book:*")
    authors = r.scan_iter(match="Author:*")
    authors = [r.hgetall(a) for a in authors]
    authors = {a["id"]: Author(**a) for a in authors}

    book_info = {b.removeprefix("Book:"): r.hgetall(b) for b in books}
    return [
        Book(id=id, title=book["title"], author=authors[book["author"]])
        for id, book in book_info.items()
    ]


def get_authors(info: Info):
    r: redis.Redis = info.context["redis"]
    authors = r.scan_iter(match="Author:*")
    authors = [r.hgetall(a) for a in authors]
    authors = [Author(**a) for a in authors]

    return authors


@strawberry.type
class Query:
    books: List[Book] = strawberry.field(resolver=get_books)
    book: Book = strawberry.field(resolver=get_book)
    authors: List[Author] = strawberry.field(resolver=get_authors)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(
        self,
        id: strawberry.ID,
        title: str,
        author_id: strawberry.ID,
        author_name: str,
        info: Info,
    ) -> Book:
        r: redis.Redis = info.context["redis"]

        r.hset(f"Book:{id}", mapping={"author": author_id, "title": title})
        if not r.exists(f"Author:{author_id}"):
            r.hset(
                f"Author:{author_id}", mapping={"id": author_id, "name": author_name}
            )
        r.sadd(f"BooksByAuthor:{author_id}", id)
        return Book(id=id, title=title, author=Author(id=author_id, name=author_name))


schema = strawberry.Schema(Query, Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
