FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
RUN groupadd -r groupbot && useradd -r -g groupbot botuser 
WORKDIR /r4bot
RUN chown botuser:groupbot /r4bot 
RUN pip install --upgrade pip wheel
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
COPY --chown=botuser:groupbot . .
USER botuser
CMD ["python", "aiogram_run.py"]
