FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY bonus/requirements.txt /app/bonus/requirements.txt
RUN pip install --no-cache-dir -r /app/bonus/requirements.txt

COPY bonus /app/bonus

WORKDIR /app/bonus
