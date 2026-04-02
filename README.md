# HullCheck 🚢

Automatically checks and updates Docker containers when new images are available.

## Requirements
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Docker

## Installation
```bash
git clone https://github.com/abhiram6121/hullcheck.git
cd hullcheck
uv sync
```

## Usage
```bash
uv run main.py
```

## Automate with cron
```bash
0 2 * * * cd /path/to/hullcheck && uv run main.py >> /var/log/hullcheck.log 2>&1
```

## What it does
- Checks all running containers for image updates
- Pulls new images when available
- Recreates Compose containers automatically
- Skips local/private images gracefully
