# BirdNET Containerized Monitoring System

[![Unit test](https://github.com/swe-students-spring2026/4-containers-lime_llamas/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-lime_llamas/actions/workflows/lint.yml)

A containerized bird sound monitoring system built with Flask, MongoDB, Docker Compose, and BirdNET. The system records and processes bird audio data, identifies bird species through machine learning, stores results in MongoDB, and displays recent detections in a web dashboard.

## Team

- [Laura Liu](https://github.com/lauraliu518)
- [Ethan Demol](https://github.com/ethandemol)
- [Yutong Liu](https://github.com/Abbyyyt)
- [Owen Zhang](https://github.com/owenzhang2004)
- [Howard Xia](https://github.com/hewlett-packard-lovecraft)

## Task Board

Project board: [GitHub Project 118](https://github.com/orgs/swe-students-spring2026/projects/118)

## Features

- Multi-container architecture managed with Docker Compose
- MongoDB database shared by the web app and machine-learning client
- Flask dashboard for viewing stored bird detections
- BirdNET-based machine-learning pipeline for bird sound classification
- Persistent database storage through Docker volumes
- Automatic MongoDB initialization with collections and indexes
- CI checks for formatting and linting with GitHub Actions

## Repository Structure

```text
.
├── web-app/                  # Flask web application
├── machine-learning-client/  # Bird sound classification client
├── database/                 # MongoDB initialization scripts
├── .github/workflows/        # CI workflows
├── docker-compose.yml        # Multi-container orchestration
└── README.md
```

## Architecture

The system consists of three services:

1. **mongodb**  
   Stores recording metadata and bird detection results.

2. **web-app**  
   Provides a Flask-based dashboard for viewing stored detections.

3. **machine-learning-client**  
   Processes audio input, runs BirdNET classification, and writes results to MongoDB.

All services run on the same Docker Compose network and communicate using Docker service names.

## Database Setup

The project uses MongoDB running in Docker.

MongoDB is configured in `docker-compose.yml` with:

- image: `mongo:7`
- container name: `birdnet-mongodb`
- port mapping: `27017:27017`
- persistent volume for stored data
- an initialization script mounted into `/docker-entrypoint-initdb.d`

The application database is:

- `birdnet_db`

The initialization script is located at:

    database/mongo-init.js

It automatically:

- selects the `birdnet_db` database
- creates the `recordings` collection
- creates the `detections` collection
- creates indexes for efficient querying

## Environment Variables

Both the web app and the machine-learning client use the following environment variables:

    MONGO_URI=mongodb://admin:admin123@mongodb:27017/?authSource=admin
    MONGO_DB_NAME=birdnet_db

Because the services run inside Docker Compose, the hostname `mongodb` is used instead of `localhost`.

Example environment files are included in:

- `web-app/.env.example`
- `machine-learning-client/.env.example`

To create local environment files, copy each example file to `.env` inside the same directory.

## Installation and Setup

### 1. Clone the repository

    git clone REPLACE_WITH_YOUR_REPO_URL
    cd 4-containers-lime_llamas

### 2. Create environment files

Create the following files:

- `web-app/.env`
- `machine-learning-client/.env`

Use the provided example files as templates:

- `web-app/.env.example`
- `machine-learning-client/.env.example`

### 3. Start the full system

    docker compose up --build

This starts:

- MongoDB
- the Flask web app
- the machine-learning client

### 4. Stop the system

    docker compose down

## Local Development

Each subsystem uses Pipenv for dependency management.

### Web app

    cd web-app
    pipenv install
    pipenv run black .
    pipenv run pylint app.py

### Machine-learning client

    cd machine-learning-client
    pipenv install
    pipenv run black .
    pipenv run pylint .

## Code Quality and CI

The repository uses GitHub Actions to run automated checks on pushes and pull requests.

The CI workflow includes:

- `black` for formatting checks
- `pylint` for linting checks

These checks are defined in:

    .github/workflows/lint.yml

## Data Model

The MongoDB database contains two main collections:

### `recordings`

Stores metadata about processed audio recordings, such as:

- recording time
- device or source information
- file metadata

### `detections`

Stores BirdNET prediction results, such as:

- detected species name
- confidence score
- associated recording reference
- detection timestamps

This structure allows the machine-learning client to write processed results while the web app reads and displays them efficiently.

## Usage

After starting the system with Docker Compose:

- the machine-learning client processes bird audio data
- classification results are stored in MongoDB
- the web app reads the stored data and displays recent detections

This creates a complete end-to-end pipeline from audio analysis to dashboard visualization.

## Technologies Used

- Python
- Flask
- MongoDB
- PyMongo
- Docker
- Docker Compose
- Pipenv
- BirdNET
- GitHub Actions
- Black
- Pylint
