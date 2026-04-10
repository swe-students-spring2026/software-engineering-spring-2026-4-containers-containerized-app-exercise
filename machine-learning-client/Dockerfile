FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy

COPY . .
CMD ["python", "main.py"]