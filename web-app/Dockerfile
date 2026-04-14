FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/runtime

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]