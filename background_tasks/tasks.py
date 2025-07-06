from asyncio import sleep as async_sleep

from PIL import Image
import os

from src.api.dependecy import get_db_manager


def save_resized_images_f(file_path: str, sizes=(1000, 500, 300), output_dir="src/static/images/"):
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

        new_filename = f"{base_filename}_{width}_f.jpg"
        save_path = os.path.join(output_dir, new_filename)

        resized.save(save_path, format="JPEG", quality=85)
        saved_files.append(new_filename)

    return saved_files


async def resend_email():
    while True:
        async for db in get_db_manager():
            await db.bookings.get_today_booking()
            print("send email")
        await async_sleep(10)
