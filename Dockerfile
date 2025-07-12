FROM python:3.11-slim-bookworm

WORKDIR /app

# Устанавливаем только минимально необходимые пакеты одной командой
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Устанавливаем готовые wheel пакеты для ускорения
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=all -r requirements.txt

# Копируем приложение
COPY . .

# Порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
