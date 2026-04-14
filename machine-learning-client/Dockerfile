FROM python:3.11-slim



WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

ADD . .

CMD ["python", "src/tracker.py", "--api-url", "http://web-app:5000/api/gaze"]