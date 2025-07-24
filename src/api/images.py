from pathlib import Path

from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException
import shutil

from background_tasks.tasks import save_resized_images_f
from src.services.image import ImageService

router = APIRouter(prefix="/images", tags=["Загрузка изображений"])


@router.post(
    "",
    summary="Загрузка изображения",
    description=(
        "Загружает изображение, сохраняет его на диск и инициирует две параллельные обработки:\n\n"
        "1. `ImageService.save_resized_images(path)` — отправляет задачу в очередь Celery (отдельный процесс);\n"
        "2. `save_resized_images_f(path)` — запускается как фоновая задача FastAPI (в отдельном потоке).\n\n"
        "Обе обработки предназначены для создания уменьшенных копий изображения или других модификаций.\n\n"
        "Размер файла ограничен до 2 мегабайт (на уровне nginx)."
    ),
)
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


@router.get(
    "",
    summary="Список всех файлов в /images",
    description=(
        "Возвращает список всех файлов, находящихся в директории `/images`, \n\n"
        "Если папка отсутствует или в ней нет файлов, возвращается ошибка 404."
    ),
)
async def list_all_image_files():
    images_folder = Path("src/static/images")
    if not images_folder.exists():
        raise HTTPException(status_code=404, detail="Папка /images не найдена")

    all_files = [str(p.relative_to(images_folder)) for p in images_folder.rglob("*") if p.is_file()]
    if not all_files:
        raise HTTPException(status_code=404, detail="Файлы не найдены")
    return {"files": all_files}
