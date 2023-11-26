import json

import redis

from fastapi import FastAPI

from database.operations import (db_get_books, db_new_book_add,
                                 db_change_author_book, db_delete_book,
                                 db_get_authors, db_new_authors_add)
from models import Book, Author
from backtasks import processing_request

BOOKS_LIMIT = 10
AUTHORS_LIMIT = 10

tasks_list = []

app = FastAPI(
    title="Library"
)


@app.get("/")
def cel_res():
    dist_obj_in = {
        "test": "ok"
    }
    json_obj_in = json.dumps(dist_obj_in, indent=4)
    status = processing_request.delay(json_obj_in)
    return status.id


def serial_processing_deserial_book(book: Book):
    """Сериализация, обработка, и десериализация полученных данных"""
    # сериализация в json
    json_obj_in = json.dumps(book.model_dump(), indent=4)
    # передаём данные в формате json в симуляцию ML-модели и получаем
    # данные из модели в том же формате
    json_obj_out = processing_request(json_obj_in)
    # десериализация из json
    data_dict_out = json.loads(json_obj_out)
    return Book(**data_dict_out)


def serial_processing_book(book: Book, task_type: str = "root"):
    """Сериализация и отправка на обработку данных в ML-модель"""
    # сериализация в json
    json_obj_in = json.dumps(book.model_dump(), indent=4)
    # передаём данные в формате json в симуляцию ML-модели
    response = processing_request.delay(json_obj_in, task_type)
    return response.id


def serial_processing_deserial_author(author: Author):
    """Сериализация, обработка, и десериализация полученных данных"""
    # сериализация в json
    json_obj_in = json.dumps(author.model_dump(), indent=4)
    # передаём данные в формате json в симуляцию ML-модели и получаем
    # данные из модели в том же формате
    json_obj_out = processing_request(json_obj_in)
    # десериализация из json
    data_dict_out = json.loads(json_obj_out)
    return Author(**data_dict_out)


@app.get("/processing")
def processing_tasks_user():
    """Запрос информации по выполнению задач"""
    if tasks_list == []:
        return False
    pattern_str = tasks_list.pop()
    r = redis.Redis("localhost", 6379)
    string = r.get((r.keys(pattern=f"*{pattern_str}*"))[0])
    string_json = json.loads(string)
    task_type = string_json["result"]["task_type"]
    data = json.loads(string_json["result"]["request"])
    if task_type == "get_books":
        book_out = Book(**data)
        return {"task_type": task_type,
                "result": db_get_books(book_out.limit)}
    return {"task_type": task_type,
            "result": data}


@app.get("/books")
def get_books(limit: int = BOOKS_LIMIT):
    """Запрашиваем последние добавленные в библиотеку книги."""
    # создаём обьект класса Book здесь, т.к.
    # request with GET/HEAD method cannot have body
    book = Book()
    book.limit = limit
    response = serial_processing_book(book, "get_books")
    tasks_list.append(response)
    return {"task_id": response}


@app.post("/books")
def new_book_add(book: Book, author_id: int, book_title: str,
                 description: str):
    """Добавляем новую книгу в библиотеку."""
    book.author_id = author_id
    book.book_title = book_title
    book.description = description
    book_out = serial_processing_deserial_book(book)
    return db_new_book_add(book_out.author_id, book_out.book_title,
                           book_out.description)


@app.put("/books")
def сhange_author_book(book: Book, book_id: int, new_autor_id: int):
    """Меняем автора книги по id книги."""
    book.id = book_id
    book.author_id = new_autor_id
    book_out = serial_processing_deserial_book(book)
    return db_change_author_book(book_out.id, book_out.author_id)


@app.delete("/books")
def delete_book(book: Book, id: int):
    """Удаляем книгу по id книги."""
    book.id = id
    book_out = serial_processing_deserial_book(book)
    return db_delete_book(book_out.id)


@app.get("/authors")
def get_authors(limit: int = AUTHORS_LIMIT):
    """Выводим последних добавленных авторов."""
    author = Author()
    author.limit = limit
    author_out = serial_processing_deserial_author(author)
    return db_get_authors(author_out.limit)


@app.post("/authors")
def new_authors_add(author: Author, fio: str, biography: str):
    """Добавляем нового автора."""
    author.fio = fio
    author.biography = biography
    author_out = serial_processing_deserial_author(author)
    return db_new_authors_add(author_out.fio, author_out.biography)
