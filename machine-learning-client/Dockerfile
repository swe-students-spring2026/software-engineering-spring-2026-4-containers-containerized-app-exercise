FROM tensorflow/tensorflow:latest

WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1

RUN rm -rf /var/lib/apt/lists/*


# COPY Pipfile Pipfile.lock ./

# RUN pip install pipenv

# RUN pipenv requirements > requirements.txt


COPY requirements.txt ./

RUN pip install --ignore-installed -r requirements.txt

COPY . ./

RUN python config.py

#CMD ["gunicorn", "--bind", "0.0.0.0:8000",  "--worker-tmp-dir","/dev/shm/", "--workers", "65", "--threads", "260" , "app:app"]

#CMD ["gunicorn",  "--bind", "0.0.0.0:8000",  "--worker-tmp-dir","/dev/shm/", "--workers", "4", "--threads", "8" , "app:app"]

CMD ["flask",  "run", "--host=0.0.0.0", "--port", "8000"]
