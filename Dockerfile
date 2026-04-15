FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
ADD . .
EXPOSE 3000

# Run app.py when the container launches
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" "--port=3000"]