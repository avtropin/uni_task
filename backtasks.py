from time import sleep

from celery import Celery

# from models import TaskData

celery = Celery(__name__,
                broker='redis://localhost:6379',
                backend='redis://localhost:6379')


@celery.task
def processing_request(request, task_type: str = "root"):
    # создаём видимость обработки полученных данных ML-моделью
    sleep(5)
    return {"task_type": task_type, "request": request}
