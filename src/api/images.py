from pathlib import Path

from fastapi import APIRouter, UploadFile, BackgroundTasks
import shutil

from fastapi.responses import JSONResponse

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

    return {"status": "ok"}


IMAGES_FOLDER = Path("src/static/images")

@router.get("", summary="Список всех файлов в /images")
async def list_all_image_files():
    if not IMAGES_FOLDER.exists():
        return JSONResponse(status_code=404, content={"detail": "Папка не найдена"})

    all_files = [
        str(p.relative_to(IMAGES_FOLDER))
        for p in IMAGES_FOLDER.rglob("*")
        if p.is_file()
    ]
    return {"files": all_files}