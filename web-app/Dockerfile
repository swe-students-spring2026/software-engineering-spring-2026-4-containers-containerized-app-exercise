FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY Pipfile ./
RUN pip install pipenv && pipenv install --system --skip-lock

COPY . .

EXPOSE 5000

ENV MONGO_URI=mongodb://mongodb:27017/
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]
