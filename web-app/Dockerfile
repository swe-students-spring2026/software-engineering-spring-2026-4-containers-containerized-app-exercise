FROM python:3.11-slim
<<<<<<< HEAD
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy
ADD . .
EXPOSE 5000
CMD ["python3", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
=======

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
>>>>>>> d3c46829bdf67506af6ff34ac8f4670e71708b4a
