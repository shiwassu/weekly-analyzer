FROM python:3.10-slim

RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pytesseract numpy Pillow python-multipart

COPY . /app

EXPOSE 7860

CMD ["python", "app.py"]
