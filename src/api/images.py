from fastapi import APIRouter, UploadFile, BackgroundTasks
import shutil

from background_tasks.tasks import save_resized_images_f
from src.services.image import ImageService

router = APIRouter(prefix="/images", tags=["Загрузка изображений"])

@router.post("")
def upload_image(file: UploadFile, background_task: BackgroundTasks):
    # todo Нужно сделать интерфейс что бы передавать file в сервис
    path = f"src/static/images/{file.filename}"
    with open(path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    ImageService().save_resized_images(path)

    background_task.add_task(
        save_resized_images_f, path
    )  # new_case: фоновая задачи fastapi, создает поток.
