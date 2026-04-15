FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg portaudio19-dev && rm -rf /var/lib/apt/lists/*
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
COPY . .
CMD ["python", "-m", "app.pipeline"]