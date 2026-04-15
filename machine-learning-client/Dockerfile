FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY Pipfile ./
RUN pip install pipenv && pipenv install --system --skip-lock

COPY . .

ENV MONGO_URI=mongodb://mongodb:27017/

CMD ["python", "main.py"]
