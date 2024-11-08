# EddyAI
EddyAI backbone script for completion request and post-processing model output

## Setup project
```bash
# clone this repo and then setup the .env file

cp .env.example .env
```

## Running with Docker
```bash
docker compose -p eddy-builder-ai up -d --build
```

## Running without Docker
**Requirements:**
- Python 3.12

```bash
python3 -m venv .venv
```

```bash
# Windows (bash)
source .venv/Scripts/activate

# Linux or Mac
source .venv/bin/activate
```

```bash
pip install --no-cache-dir -r requirements.txt
```

```bash
python wsgi.py
```
