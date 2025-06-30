from time import sleep

from celery import Task

from src.celery_tasks.celery_app import celery_inst
from PIL import Image
import os

task1: Task


@celery_inst.task
def task1():
    sleep(5)
    print("такса1 выполнена")


save_resized_images: Task



from celery import shared_task

@celery_inst.task
def save_resized_images(file_path: str, sizes=(1000, 500, 300), output_dir="src/static/images/"):
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Открытие изображения с диска
        with open(file_path, "rb") as f:
            image = Image.open(f)
            image.load()  # загрузка изображения в память (важно для некоторых форматов)
    except Exception as e:
        raise ValueError(f"Не удалось открыть изображение: {e}")

    # Преобразование в RGB, если нужно
    if image.mode != "RGB":
        image = image.convert("RGB")

    base_filename = os.path.splitext(os.path.basename(file_path))[0]

    saved_files = []

    for width in sizes:
        ratio = width / image.width
        height = int(image.height * ratio)
        resized = image.resize((width, height))

        new_filename = f"{base_filename}_{width}.jpg"
        save_path = os.path.join(output_dir, new_filename)

        resized.save(save_path, format="JPEG", quality=85)
        saved_files.append(new_filename)

    return saved_files

