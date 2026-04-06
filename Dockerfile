FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
RUN groupadd -r groupbot && useradd -r -g groupbot botuser
WORKDIR /r4bot
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip wheel
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
COPY . .
USER botuser
CMD ["python", "aiogram_run.py"]
