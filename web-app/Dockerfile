FROM python:3.12.10

WORKDIR /app

RUN pip install --no-cache-dir pipenv
COPY Pipfile /app/
RUN pipenv install --system --skip-lock
RUN pip cache purge

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]
