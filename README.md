# SignBridge - Sign Language Recognition Dashboard + Containerized App

[![CI Subsystems](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/ci.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/ci.yml)
[![lint-free](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/lint.yml)

## App Description:
Introduction: SignBridge is an educational web platform that helps users understand sign language recognition results through an interactive dashboard.

Product Vision: The app aims to make sign language recognition more useful in educational settings, making sign language technology more understandable, accessible, and meaningful for real users.

## Product Overview
SignBridge is containerized computer vision application designed to recognize and translate sign language gestures in real-time. The project uses a Machine Learning client (utilizing OpenCV and a Convolutional Neural Network trained on the Sign Language MNIST dataset) to detect American Sign Language (ASL) alphabet gestures from a video feed, and saves the classification results to a MongoDB database. A Flask web dashboard reads this database to show the translated gestures and confidence scores in real-time.

## Team Members
- [Hollan Yuan](https://github.com/hwyuanzi)
- [Jonas Chen](https://github.com/JonasChenJusFox)
- [Ruby Zhang](https://github.com/yz10113-tech)
- [Suri Su](https://github.com/suri-zip)
- [Zeyue Xu](https://github.com/zeyuexu123)

## Architecture
This project is containerized using Docker and is split into three main parts, run together using Docker Compose:

The application consists of three main services:

```text
+---------------------------+      +-----------------------+      +---------------------------+
| Machine Learning Client   | ---> | MongoDB Database      | ---> | Flask Web Dashboard       |
| OpenCV + CNN Inference    |      | Stores Predictions    |      | Visualizes Results        |
+---------------------------+      +-----------------------+      +---------------------------+
```

1. **Machine Learning Client**: The machine learning client is a Python-based service that captures video frames with OpenCV, processes the hand region, and classifies gestures using a custom CNN model trained on the Sign Language MNIST dataset.
2. **Web App**: The web app is built with Flask and provides an interactive dashboard for viewing live prediction results, confidence scores, and historical gesture data.
3. **Database**: The database uses MongoDB to store timestamped prediction results, confidence scores, and related metadata, allowing the system to retrieve and display both recent and past predictions.

## Project Structure

```bash
web-app/
├── app.py
├── routes/
│   ├── api.py
│   └── pages.py
├── services/
│   └── prediction_service.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── history.html
├── static/
│   ├── css/
│   └── js/
├── db/
│   └── mongo.py
└── tests/
```

## Running the Application

Follow these steps to run the project via Docker Compose.

**1. Enviroment Setup**
Before running the project, make sure you have the following installed:
  - Git
  -[Docker](https://www.docker.com/products/docker-desktop/?utm_source=chatgpt.com)
  - Docker Compose

**2. Clone the repository**
```bash
git clone https://github.com/swe-students-spring2026/4-containers-next_team.git
cd 4-containers-next_team
```

**3. Provide a sample video**
To avoid hardware permission issues with webcams inside Docker containers, our ML client processes a sample video feed for testing. You need to provide a short video of hand gestures or create a placeholder file in `machine-learning-client/data/raw/` *before* running docker-compose.
```bash
# Ensure the model directory exists
mkdir -p machine-learning-client/src/data/processed/
mkdir -p machine-learning-client/src/data/raw/

# Place your trained weights file here (e.g., model.pth for PyTorch or model.h5 for Keras)
# Path should look like: machine-learning-client/data/model/sign_language_model.pth
```
Download the dataset from:

https://www.kaggle.com/datasets/datamunge/sign-language-mnist?resource=download

and place it in 

machine-learning-client/src/data/raw/

**3.5. Train the model**
```bash
cd machine-learning-client\src

python src_main.py
```

**4. Set up environment variables**
We use a `.env` file for config. Create it by copying the template we provided:
```bash
cp .env.example .env
```
Docker compose will use this file. The default values inside are fine for running the app locally, but the file just needs to be there.

**5. Start the containers**
Build and start everything:
```bash
docker-compose up --build
```
*(You can add `-d` at the end to run them in the background).*

**6. View the app and logs**
- **Web App:** Go to [http://localhost:5001](http://localhost:5001) in your browser to see the dashboard.
- **ML Client Logs:** To check if the machine learning client is running and processing the video, open a new terminal and run:
  ```bash
  docker logs ergonomics_ml
  ```
- **Database:** MongoDB runs on port 27017 automatically.

**7. Shutting down**
When you're done, stop the containers properly so your database data isn't lost:
```bash
docker-compose down
```

## Development Workflow

We use a basic Agile workflow for this project:

- **Task Board**: We track tasks using the GitHub Projects board linked to this repo.
- **Dependencies**: Each subsystem (`web-app` and `machine-learning-client`) manages its own dependencies using Pipenv to keep things separated.
- **CI / CD Pipeline**: We use Github Actions for CI. Any pull request has to pass Pytest (with >80% coverage) and linting checks (Pylint & Black) before we can merge it into the main branch.
