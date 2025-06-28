from celery import Celery

from src.config import settings

"""
Запуск
celery --app=src.celery_tasks.celery_app:celery_inst worker --loglevel INFO
"""
celery_inst = Celery(
    main="tasks",
    broker=settings.REDIS_URL,
    include=["src.celery_tasks.tasks"]

)
