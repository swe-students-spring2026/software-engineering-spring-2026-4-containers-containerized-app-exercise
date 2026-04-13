
FROM python:3.10-slim
 

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
 

COPY . .
 
EXPOSE 5001
 
CMD ["python", "ml_client.py"]