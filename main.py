import json

from redis import Redis
from fastapi import FastAPI

from database.operations import (db_get_books, db_new_book_add,
                                 db_change_author_book, db_delete_book,
                                 db_get_authors, db_new_authors_add)
from models import Book, Author
from backtasks import processing_request

BOOKS_LIMIT = 10
AUTHORS_LIMIT = 10

tasks_list = []  # имитация хранения списка ключей запросов на стороне клиента

# список задач, заданный в порядке приоритетности
dict_task_type = {
    "del": [],  # задачи на удаление
    "put": [],  # задачи на изменение
    "pos": [],  # задачи на добавление
    "get": []  # задачи на запрос данных
}


app = FastAPI(
    title="Library"
)


def grouping_by_queries(task_type: str, data):
    """Группируем по запросам"""
    dict_task_type[task_type[0:3]].append({"task_type": task_type,
                                           "data": data})


def prioritization_of_tasks():
    """Запускаем задачи на обработку в ML-модель согласно приоритетам"""
    for key in dict_task_type.keys():
        while dict_task_type[key] != []:
            data_task = dict_task_type[key].pop()
            response = processing_request.delay(data_task["data"],
                                                data_task["task_type"])
            tasks_list.append(response.id)


def serial_processing_book(book: Book, task_type: str = "root"):
    """Сериализация и отправка на группировку"""
    # сериализация в json
    json_obj_in = json.dumps(book.model_dump(), indent=4)
    # отправляем на группировку по запросам
    grouping_by_queries(task_type, json_obj_in)


def serial_processing_author(author: Author, task_type: str = "root"):
    """Сериализация и отправка на обработку данных в ML-модель"""
    # сериализация в json
    json_obj_in = json.dumps(author.model_dump(), indent=4)
    # отправляем на группировку по запросам
    grouping_by_queries(task_type, json_obj_in)


@app.get("/processing")
def processing_tasks_user():
    """Запрос информации по выполнению задач"""
    if tasks_list == []:
        return False
    list_task_complete = []
    while tasks_list != []:
        pattern_str = tasks_list.pop()
        r = Redis("uni_task-redis-1", 6379)
        try:
            string = r.get((r.keys(pattern=f"*{pattern_str}*"))[0])
        except Exception:
            tasks_list.append(pattern_str)
            continue
        string_json = json.loads(string)
        task_type = string_json["result"]["task_type"]
        data = json.loads(string_json["result"]["request"])
        if task_type == "get_books":
            book_out = Book(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_get_books(book_out.limit)})
        if task_type == "post_new_book_add":
            book_out = Book(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_new_book_add(book_out.author_id,
                                          book_out.book_title,
                                          book_out.description)})
        if task_type == "put_сhange_author_book":
            book_out = Book(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_change_author_book(book_out.id,
                                                book_out.author_id)})
        if task_type == "delete_book":
            book_out = Book(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_delete_book(book_out.id)})
        if task_type == "get_authors":
            author_out = Author(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_get_authors(author_out.limit)})
        if task_type == "post_new_authors_add":
            author_out = Author(**data)
            list_task_complete.append({
                "task_type": task_type,
                "result": db_new_authors_add(author_out.fio,
                                             author_out.biography)})
        if task_type == "root":
            list_task_complete.append({"task_type": task_type,
                                       "result": data})
    return list_task_complete


@app.get("/books")
def get_books(limit: int = BOOKS_LIMIT):
    """Запрашиваем последние добавленные в библиотеку книги."""
    # создаём обьект класса Book здесь, т.к.
    # request with GET/HEAD method cannot have body
    book = Book()
    book.limit = limit
    serial_processing_book(book, "get_books")
    prioritization_of_tasks()
    return {"status": "ok"}


@app.post("/books")
def new_book_add(book: Book, author_id: int, book_title: str,
                 description: str):
    """Добавляем новую книгу в библиотеку."""
    book.author_id = author_id
    book.book_title = book_title
    book.description = description
    serial_processing_book(book, "post_new_book_add")
    prioritization_of_tasks()
    return {"status": "ok"}


@app.put("/books")
def сhange_author_book(book: Book, book_id: int, new_autor_id: int):
    """Меняем автора книги по id книги."""
    book.id = book_id
    book.author_id = new_autor_id
    serial_processing_book(book, "put_сhange_author_book")
    prioritization_of_tasks()
    return {"status": "ok"}


@app.delete("/books")
def delete_book(book: Book, id: int):
    """Удаляем книгу по id книги."""
    book.id = id
    serial_processing_book(book, "delete_book")
    prioritization_of_tasks()
    return {"status": "ok"}


@app.get("/authors")
def get_authors(limit: int = AUTHORS_LIMIT):
    """Выводим последних добавленных авторов."""
    author = Author()
    author.limit = limit
    serial_processing_author(author, "get_authors")
    prioritization_of_tasks()
    return {"status": "ok"}


@app.post("/authors")
def new_authors_add(author: Author, fio: str, biography: str):
    """Добавляем нового автора."""
    author.fio = fio
    author.biography = biography
    serial_processing_author(author, "post_new_authors_add")
    prioritization_of_tasks()
    return {"status": "ok"}
