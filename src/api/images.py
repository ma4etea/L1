from fastapi import APIRouter, UploadFile, BackgroundTasks
import shutil

from background_tasks.tasks import save_resized_images_f
from src.celery_tasks.tasks import save_resized_images

router = APIRouter(prefix="/images", tags=["Загрузка изображений"])


@router.post("")
def upload_image(file: UploadFile, background_task: BackgroundTasks):
    path = f"src/static/images/{file.filename}"
    with open(path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    save_resized_images.delay(path)  # new_case: задача для celery создает процесс

    background_task.add_task(
        save_resized_images_f, path
    )  # new_case: фоновая задачи fastapi создает поток
