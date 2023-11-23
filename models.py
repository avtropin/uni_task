from typing import Union
from time import sleep

from pydantic import BaseModel, constr


class MLModel():
    """Симуляция ML-модели"""

    def processing_request(self, request):
        # создаём видимость обработки полученных данных
        sleep(5)
        return request


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
