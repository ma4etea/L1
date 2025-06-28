from time import sleep

from celery import Task

from src.celery_tasks.celery_app import celery_inst

task1: Task
@celery_inst.task
def task1():
    sleep(5)
    print("такса1 выполнена")