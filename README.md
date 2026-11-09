# TaskFlow Task Manager

A responsive, server-rendered task manager built for a Python full-stack learning project.

## Deployment

The live application is deployed on Render:

[Open TaskFlow Live Demo](https://taskflow-task-manager-snck.onrender.com)

The included `render.yaml` contains the deployment configuration.

## Features

- FastAPI routes with Jinja2 template inheritance
- SQLAlchemy ORM with SQLite persistence
- Create, read, update, delete, complete, and reopen tasks
- Dashboard statistics and completion percentage
- Search, status/priority filtering, and sorting
- Safe image attachments with UUID filenames, MIME/content validation, and a 2 MB limit
- Responsive SaaS-style interface for desktop and mobile

## Setup on Windows PowerShell

```powershell
cd task_manager
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000.

## Architecture

- `main.py`: application creation, static mounting, and table initialization
- `database.py`: SQLAlchemy engine, declarative base, and request sessions
- `models.py`: database entities
- `schemas.py`: Pydantic form validation models
- `crud.py`: database operations and statistics
- `routers/tasks.py`: HTML routes and upload validation
- `templates/`: reusable Jinja2 pages and partials
- `static/`: CSS and JavaScript assets
- `uploads/`: runtime image storage, ignored by Git

## Verification

```powershell
python -c "from main import app; print(app.title)"
```
