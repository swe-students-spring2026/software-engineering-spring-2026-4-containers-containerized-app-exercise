# Ergonomics & Posture Monitor

[![CI Subsystems](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/ci.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/ci.yml)
[![lint-free](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-next_team/actions/workflows/lint.yml)

A containerized health monitoring application to help developers maintain better posture. The project uses a Machine Learning client (with OpenCV and MediaPipe) to detect poor posture like slouching from a video feed, and saves the data to a MongoDB database. A Flask web dashboard reads this database to show the posture data in real-time.

## Team Members
- [Hollan Yuan](https://github.com/hwyuanzi)
- [Jonas Chen](https://github.com/JonasChenJusFox)
- [Ruby Zhang](https://github.com/)
- [Suri Su](https://github.com/suri-zip)

*(Note: We will update these links later.)*

## Architecture
This project is containerized using Docker and is split into three main parts, run together using Docker Compose:
1. **Machine Learning Client**: A Python script that tracks skeletal posture using OpenCV and MediaPipe.
2. **Web App**: A Python Flask web server showing a UI dashboard.
3. **Database**: A MongoDB instance to store the timestamped posture data.

## Running the Application

Follow these steps to run the project via Docker Compose.

**1. Prerequisites**
Make sure you have Git, Docker, and Docker Compose installed. You'll need Docker Desktop running in the background.

**2. Clone the repository**
```bash
git clone https://github.com/swe-students-spring2026/4-containers-next_team.git
cd 4-containers-next_team
```

**3. Provide a sample video (Important!)**
To avoid permission issues with webcams in Docker, our ML client processes a sample video instead. Since we don't upload large videos to GitHub, you need to create a placeholder or add your own video file *before* running docker-compose.
*(Note: If you skip this, Docker will create a directory named `sample.mp4` by mistake and crash the ML container!)*
```bash
# either copy a real short video to this path, or just create a blank placeholder file:
touch machine-learning-client/sample.mp4
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
- **Web App:** Go to [http://localhost:5000](http://localhost:5000) in your browser to see the dashboard.
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
