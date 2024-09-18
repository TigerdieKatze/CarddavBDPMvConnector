FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY carddav_sync.py .

CMD ["python", "carddav_sync.py"]