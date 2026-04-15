# 🗑️ Smart Garbage Classifier

[![ML Client CI](https://github.com/swe-students-spring2026/4-containers-sexy_pandas/actions/workflows/ml_client.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-sexy_pandas/actions/workflows/ml_client.yml)
[![Web App CI](https://github.com/swe-students-spring2026/4-containers-sexy_pandas/actions/workflows/web_app.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-sexy_pandas/actions/workflows/web_app.yml)

A containerized web application that uses machine learning to classify garbage images and help users sort waste into the correct recycling bins. Users can upload an image or use their camera to capture a photo of a waste item, the system identifies the material and tells them which bin to use.

## Team

- [Celia Liang](https://github.com/liangchuxin)
- [Meili Liang](https://github.com/ml8397)
- [Qingyue Zhu](https://github.com/Kairiszqy)
- [Hanlin Yan](https://github.com/hanlinyan-dev)
- [Grace Yu](https://github.com/gy28611)

## Architecture

The system consists of three Docker containers:

- **web-app** — Flask web application (port 5001). Accepts image uploads from the browser, forwards them to the ML client, stores results in MongoDB, and renders the dashboard.
- **ml-client** — Flask inference service (port 8000). Receives images from the web app, calls the Roboflow garbage classification model, and returns predictions.
- **mongodb** — MongoDB database. Stores classification results for history and dashboard display.

```
Browser → web-app:5001 → ml-client:8000 → Roboflow API
                ↓
            MongoDB
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A Roboflow API key (sign up free at [roboflow.com](https://roboflow.com))

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/swe-students-spring2026/4-containers-sexy_pandas.git
cd 4-containers-sexy_pandas
```

### 2. Configure environment variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```
ML_MODEL_URL=https://serverless.roboflow.com
ML_MODEL_API_KEY=your_roboflow_api_key_here
ML_MODEL_ID=garbage-classification-3/2
MONGO_URI=mongodb://mongodb:27017/
DB_NAME=garbage_classifier
```

### 3. MongoDB

MongoDB runs inside its own Docker container using the official image so no local installation is required. It starts automatically when you run `docker-compose up`.

The database `garbage_classifier` and the `detections` collection are created automatically on first use. No starter data needs to be imported. The system begins populating the database as soon as users start classifying images.

If you wish to run MongoDB manually without docker-compose:

```bash
docker run --name mongodb -d -p 27017:27017 mongo
```

### 4. Start all containers

```bash
docker-compose up --build
```

This starts all three containers together. The web app will be available at [http://localhost:5001](http://localhost:5001).

### 5. Stop the system

```bash
docker-compose down
```

To also remove stored database data:

```bash
docker-compose down -v
```

## Usage

1. Open [http://localhost:5001](http://localhost:5001) in your browser.
2. Upload an image of a waste item using **Choose Image**, or click **Open Camera** to use your webcam.
3. Click **Start Classification** to identify the item.
4. The result shows the waste category and which bin to use (Blue / Green / Gray).
5. View your classification history at [http://localhost:5001/history](http://localhost:5001/history).

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ML_MODEL_URL` | Roboflow inference server URL | `https://serverless.roboflow.com` |
| `ML_MODEL_API_KEY` | Your Roboflow API key | *(required)* |
| `ML_MODEL_ID` | Roboflow model ID and version | `garbage-classification-3/2` |
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017/` |
| `DB_NAME` | MongoDB database name | `garbage_classifier` |

Secret files (`.env`) are not included in version control. See `.env.example` for the required format. An example file with dummy values is provided at `.env.example`.

## Running Tests

### ML Client

```bash
cd machine-learning-client
pip install -r requirements.txt
coverage run -m pytest ../test/ -v
coverage report
```

### Web App

```bash
cd web-app
pip install -r requirements.txt
pytest test/ -v
```

## Project Structure

```
├── docker-compose.yml
├── .env.example
├── machine-learning-client/
│   ├── app.py              # Flask inference API
│   ├── database.py         # MongoDB connection and save logic
│   ├── ml_client.py        # Legacy capture/inference loop
│   ├── dockerfile
│   └── requirements.txt
├── web-app/
│   ├── app.py              # Flask web application
│   ├── templates/          # Jinja2 HTML templates
│   ├── static/             # CSS
│   ├── Dockerfile
│   └── requirement.txt
├── test/
│   └── test_ml.py          # ML client unit tests
└── web-app/test/
    └── test_app.py         # Web app unit tests
```
