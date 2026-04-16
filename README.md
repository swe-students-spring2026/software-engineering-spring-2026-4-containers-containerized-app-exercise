![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# SpeechCoach

SpeechCoach is a containerized speech analysis application that allows users to record and submit speeches through a web app, process those speeches with a machine learning client, and store results in MongoDB. The purpose of this app is to aid the user in getting better at speeches by counting their filler words while giving feedback on their speed and volume.

The system includes a Flask web application, a machine learning service for speech analysis, and Docker-based containerization for local development and deployment.

## Features

### Web App
- User signup and login
- Session-based authentication
- Dashboard displaying previous speeches
- Record page for uploading or recording speech audio
- Delete speeches from the dashboard

### Machine Learning Client
- Receives submitted audio for analysis
- Uses Whisper for transcription
- Computes:
  - filler word count
  - words per minute
  - average volume
  - pitch variance
  - speech duration
- Stores results in MongoDB
- Provides API endpoints for health checks and analysis

## Repository Structure

    .
    ├── machine-learning-client/
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── db.py
    │   ├── ml_client.py
    │   ├── test_db.py
    │   ├── tests/
    │   │   └── test_ml_client.py
    │   └── readme.txt
    ├── web-app/
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── app.py
    │   ├── db.py
    │   ├── env.example
    │   ├── static/
    │   │   └── styles.css
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── dashboard.html
    │   │   ├── login.html
    │   │   ├── record.html
    │   │   └── signup.html
    │   ├── tests/
    │   │   └── test_app.py
    │   └── readme.txt
    ├── docker-compose.yml
    ├── Pipfile
    ├── Pipfile.lock
    └── README.md


## Tech Stack

### Web App
- Python
- Flask
- Flask-Login
- PyMongo
- Requests
- HTML/CSS

### Machine Learning Client
- Python
- Flask
- OpenAI Whisper
- Librosa
- NumPy
- PyMongo

### Infrastructure
- Docker
- Docker Compose
- Pipenv
- GitHub Actions

## Requirements

- Python 3.11
- Pipenv
- Docker
- Docker Compose
- MongoDB, if running without Docker

## Environment Variables

### Web App
Create a `.env` file in `web-app/` if needed.

    Example:
    SECRET_KEY=your_secret_key
    MONGO_URI=mongodb://mongodb:27017/
    ML_CLIENT_URL=http://machine-learning-client:5001/analyze

### Machine Learning Client
    Example:
    MONGO_URI=mongodb://mongodb:27017/

### Running Locally

Start the Machine Learning Client

    cd machine-learning-client
    pipenv install
    pipenv run python ml_client.py

Start the Web App

    cd web-app
    pipenv install
    pipenv run python app.py

Open

    http://127.0.0.1:5000

If port 5000 is busy

    pipenv run python -c "from app import app; app.run(host='0.0.0.0', port=5002, debug=True)"

Then open

    http://127.0.0.1:5002

### Running with Docker

Build and start all services

    docker-compose up --build

Stop services

    docker-compose down

## API Endpoints

### Web App Routes
- `GET /login` – login page
- `POST /login` – authenticate user
- `GET /signup` – signup page
- `POST /signup` – create user
- `GET /logout` – log out user
- `GET /dashboard` – show user speeches
- `GET /record` – speech recording page
- `POST /submit` – submit speech audio
- `POST /delete/<speech_id>` – delete a speech

### Machine Learning Client Routes
- `GET /health` – health check
- `POST /analyze` – analyze uploaded speech audio

## Testing

### Web App

    cd web-app
    pipenv run pytest

### Machine Learning Client

    cd machine-learning-client
    pipenv run pytest

## Continuous Integration

The project uses GitHub Actions for CI. Checks include:
- dependency installation
- formatting with Black
- linting with Pylint
- running tests

## Team Responsibilities

- **Sasha** – web app backend
- **Chris + Samay** – frontend templates and styling
- **Claire** – machine learning client
- **Valeria** – Docker and web app container setup

## Notes

- Ports may already be in use locally; if so, run Flask apps on a different port.
- The machine learning client depends on audio-processing libraries and Whisper, which may take time to install.
- MongoDB must be running for database-dependent features and tests to work.
- Environment variable values may need to be adjusted depending on whether the app is run locally or through Docker.