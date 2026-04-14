FROM python:3.11-slim
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy
ADD . .
EXPOSE 5000
CMD ["python3", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]