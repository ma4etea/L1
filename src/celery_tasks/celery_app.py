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

celery_inst.conf.beat_schedule = {
    'run-every-10-seconds': {
        'task': 'send_msg',
        'schedule': 10.0,  # каждые 10 секунд
}
}