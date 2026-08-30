FROM python:3.11-slim

WORKDIR /service

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

CMD ["python", "-m", "app.main"]
