FROM tensorflow/tensorflow:latest

WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1

RUN rm -rf /var/lib/apt/lists/*

#RUN pip install pipenv
# COPY Pipfile Pipfile.lock ./

# RUN pipenv install --system --deploy

COPY . .
RUN pip install --ignore-installed -r requirements.txt

RUN python load_model.py

CMD ["python3", "-m", "flask",  "run", "app.py", "--host=0.0.0.0"]
