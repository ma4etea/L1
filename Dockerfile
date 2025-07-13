FROM python:3.11.13

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

#CMD ["python", "src/main.py"]
CMD alembic upgrade head; python src/main.py

# todo для селери и алембика нужно создавать свои image и копировать зависимости только для них