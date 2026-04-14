FROM tensorflow/tensorflow:latest

WORKDIR /app

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

CMD ["python3", "flask",  "run", "app.py", "--host=0.0.0.0"]