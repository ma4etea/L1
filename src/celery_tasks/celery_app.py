from celery import Celery

from src.config import settings

"""
Запуск
celery --app=src.celery_tasks.celery_app:celery_inst worker --loglevel INFO
"""
# new_case: экземпляр класса celery
celery_inst = Celery(
    main="tasks",
    broker=settings.REDIS_URL,  # new_case: указывает откуда брать таски.
    include=["src.celery_tasks.tasks"]
    # new_case: так же есть возможность ложить какой то результат в redis, какой то доп. аргумент нужно указать
)
# new_case: так вызывается задачи по расписания есть так же есть crontab который задает расписание
celery_inst.conf.beat_schedule = {
    'run-every-10-seconds': {
        'task': 'send_msg',
        'schedule': 10,  # каждые 10 секунд или можно crontab
}
}