FROM python:3.11.13

# Установка Poetry
ENV POETRY_VERSION=2.1.3
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt

# Копируем исходный код
COPY . .

#CMD ["python", "src/main.py"]
# Команда запуска
CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]

# todo для селери и алембика нужно создавать свои image и копировать зависимости только для них


