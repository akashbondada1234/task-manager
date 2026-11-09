# TaskFlow Task Manager

A responsive, server-rendered task manager built for a Python full-stack learning project.

## Live Demo

Deploy this repository on Render using the included `render.yaml` configuration. Render will provide the public application URL after deployment.

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

## LinkedIn project description

Built TaskFlow, a responsive task management application using Python, FastAPI, Jinja2, SQLAlchemy, SQLite, HTML, CSS, and JavaScript. The project includes CRUD workflows, dashboard analytics, search and filtering, task completion, and secure image uploads with validation. Through this project I strengthened my understanding of server-side rendering, ORM-based persistence, dependency injection, form handling, and responsive UI design. Developed as part of my learning journey with Fullstack Experts Academy and Innomatics Research Labs/instructors.

Suggested hashtags: `#Python #FastAPI #SQLAlchemy #SQLite #Jinja2 #FullStackDevelopment #WebDevelopment #InnomaticsResearchLabs`
