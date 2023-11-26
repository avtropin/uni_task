from typing import Union

from pydantic import BaseModel, constr


class Book(BaseModel):
    id: Union[int, None] = None
    author_id: Union[int, None] = None
    book_title: Union[constr(max_length=25), None] = None
    description: Union[constr(max_length=250), None] = None
    limit: Union[int, None] = None


class Author(BaseModel):
    id: Union[int, None] = None
    fio: Union[constr(max_length=25), None] = None
    biography: Union[constr(max_length=250), None] = None
    limit: Union[int, None] = None


class User(BaseModel):
    id: Union[int, None] = None


class TaskData(BaseModel):
    id_task: int
    user_id: Union[int, None] = None
    task_type: str
    task_result: dict
