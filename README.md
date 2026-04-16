![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![Web-app](https://github.com/swe-students-spring2026/4-containers-sleepy_pandas/actions/workflows/web-app-ci.yml/badge.svg)
# AI Speech Coach

This project is a containerized multiservice audio analysis application. A user interacts with the Flask web application, audio files are shared via a Docker volume, the machine-learning client processes the audio using a local Whisper model, and the metadata is stored in MongoDB.

## Team
- [Harry Wu](https://github.com/harrywzl)
- [Tuo Zhang](https://github.com/TuoZhang0902)
- [Claire Wu](https://github.com/clairewwwwww)
- [Karen Maza](https://github.com/KarenMazaDelgado)
- [Hanson Huang](https://github.com/Hansonhzh)

## Task Board

- [Project Task Board](https://github.com/orgs/swe-students-spring2026/projects/92/views/1)

## Project Parts

1. `web-app/`
   The Flask frontend and browser-facing routes. Converts uploaded `.webm` audio to `.wav` using `pydub` and queues processing tasks in the database.
2. `machine-learning-client/`
   The background service that polls the database for tasks, transcribes audio using a local Whisper model (`base.en`), analyzes the text, and stores results.
3. `mongodb`
   The database container used by both services to store tasks (`commands` collection) and analysis results (`practice_sessions` collection).

## Prerequisites

  - [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Setup

### 1\. Clone the repository

```bash
git clone https://github.com/swe-students-spring2026/4-containers-sleepy_pandas.git
```

### 2\. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values, transcription is local, so an OpenAI API key is not required:

```text
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=ai_speech_coach
MONGO_COLLECTION_NAME=practice_sessions
```

### 3\. Start all containers

Build and start the application:

```bash
docker compose up -d --build
```

The web application will be available at [http://localhost:5001](https://www.google.com/search?q=http://localhost:5001).

### 4\. Stop the system

```bash
docker compose down
```

To also remove stored database data and shared audio volumes:

```bash
docker compose down -v
```

## Usage

1.  Open [http://localhost:5001](https://www.google.com/search?q=http://localhost:5001) in your browser.
2.  Upload an audio file or record a practice session directly in the UI.
3.  The system will convert the audio and queue it for processing.
4.  The background ML client will process the task and output the transcript and analysis results.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017` |
| `MONGO_DB_NAME` | MongoDB database name | `ai_speech_coach` |
| `MONGO_COLLECTION_NAME` | Collection name for saved practice sessions | `practice_sessions` |

## Running Tests

The project uses `pipenv` for dependency management. Ensure it is installed before running tests.

### ML Client

```bash
cd machine-learning-client
pipenv install --dev
pipenv run pytest tests/ -v
```

### Web App

```bash
cd web-app
pipenv install --dev
pipenv run pytest tests/ -v
```