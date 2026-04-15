FROM python:3.10-slim
WORKDIR /app

# COPY Pipfile Pipfile.lock ./

# RUN pip install pipenv

# RUN pipenv requirements > requirements.txt

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3000


CMD ["python3", "-m", "flask",  "run", "app.py", "--host=0.0.0.0", "--port", "3000"]
