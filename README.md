![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# EyeWrite MVP (Containerized App Exercise)

This repository now contains an EyeWrite MVP split into two services:

- `machine-learning-client/`: webcam + eye tracking + calibration + gaze sending
- `web-app/`: Flask UI + large keyboard + dwell typing + message + speech

## Current Structure

- `machine-learning-client/src/tracker.py`: OpenCV + MediaPipe tracking loop
- `machine-learning-client/src/gaze_math.py`: gaze feature extraction and simple calibration mapping
- `web-app/app.py`: Flask API and page server
- `web-app/templates/index.html`: typing UI
- `web-app/static/js/app.js`: gaze cursor + dwell logic + text entry + speech
- `web-app/static/css/styles.css`: responsive interface styling

## Quick Start

Start the web app first:

```bash
cd web-app
pipenv install
pipenv run python app.py
```

Then start the ML client in another terminal:

```bash
cd machine-learning-client
pipenv install
pipenv run python src/tracker.py --api-url http://127.0.0.1:5000/api/gaze
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## MVP Coverage

- Webcam feed
- Eye landmark + iris tracking
- Simple calibration
- Large keyboard with dwell typing
- Typed text box
- Space / Backspace / Clear
- Speak button
- Quick phrases (nice-to-have starter)

Standup reports:

# Standup Report - 14 April 2026

## Adam Shin @aus2005
- **did**: Web app and API integration; README and run instructions.
- **doing**: Polish Flask UI and env defaults for local vs Docker.
- **blockers**: None.

## Angelina Wu @TangelinaWu
- **did**: EyeWrite scope, reviews, ML + web coordination. 
- **doing**: Refine ML client and web app behavior.
- **blockers**: None.

## Han Xiao @vick12333
- **did**: ML accuracy experiments, `gaze_math` and tracker work Add web-app pytest.
- **doing**: Continue calibration / smoothing improvements.
- **blockers**: None.

## Alejandro
- **did**: Docker Compose, MongoDB wiring, container builds.
- **doing**: Container hardening and docs alignment.
- **blockers**: Waiting on any remaining lint or CI fixes from teammates.

## Wonden
- **did**: Web app UI work.
- **doing**: Refine typing and dwell UX.
- **blockers**: None.

# Standup Report - 15 April 2026 Evening Meeting

## Adam Shin @aus2005
- **did**: Polished UI and env.
- **doing**: Handle Linting Errors and github reversion issues.
- **blockers**: None.

## Angelina Wu @TangelinaWu
- **did**: Refined web app behavior.
- **doing**: Refine task boards.
- **blockers**: None.

## Han Xiao @vick12333
- **did**: Continued calibration / smoothing
- **doing**: Still working on calibration / smoothing improvements.
- **blockers**: None.

## Alejandro
- **did**: Worked more on the Container
- **doing**: Docs Alignment
- **blockers**: None.

## Wonden
- **did**: Refined Typing
- **doing**: Continue to work on UX. 
- **blockers**: None.

# Standup Report - 16 April 2026

## Adam Shin @aus2005
- **did**: Handled Linting Errors and github.
- **doing**: Updating ReadMe.
- **blockers**: None.

## Angelina Wu @TangelinaWu
- **did**: Finalized Task Boards.
- **doing**: Review Code.
- **blockers**: None.

## Han Xiao @vick12333
- **did**: Finished Calibration and smoothing improvements
- **doing**: Final code review.
- **blockers**: None.

## Alejandro
- **did**: Finished container and Docs Alignment.
- **doing**: Working through app to find bugs. 
- **blockers**: None.

## Wonden
- **did**: Refined UX.
- **doing**: Final checkover of project.
- **blockers**: None.
