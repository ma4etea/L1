from src.celery_tasks.tasks import save_resized_images
from src.services.base import BaseService


class ImageService(BaseService):
    def save_resized_images(self, path: str):
        # todo По правильному нужно сделать адаптер между сервис и celery
        save_resized_images.delay(path)  # new_case: задача для celery создает процесс

