from fastapi import APIRouter, UploadFile
import shutil

from src.celery_tasks.tasks import save_resized_images

router = APIRouter(prefix="/images", tags=["Загрузка изображений"])

@router.post("")
def upload_image(file: UploadFile):


    path = f"src/static/images/{file.filename}"
    with open(path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    save_resized_images.delay(path)
