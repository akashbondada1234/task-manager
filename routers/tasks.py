import mimetypes
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import TaskCreate, TaskUpdate

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
MAX_UPLOAD_SIZE = 2 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def page_context(request: Request, **values):
    return {"request": request, **values}


async def save_upload(upload: UploadFile | None) -> str | None:
    if not upload or not upload.filename:
        return None
    if upload.content_type not in ALLOWED_TYPES:
        raise ValueError("Only JPEG, PNG, GIF, and WebP images are allowed.")
    content = await upload.read(MAX_UPLOAD_SIZE + 1)
    await upload.close()
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError("Attachment must be 2 MB or smaller.")
    try:
        image = Image.open(__import__("io").BytesIO(content))
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded file is not a valid image.")
    extension = mimetypes.guess_extension(upload.content_type) or ".bin"
    filename = f"{uuid.uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return filename


@router.get("/", response_class=HTMLResponse, name="dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, sort="newest")[:5]
    return templates.TemplateResponse(request=request, name="dashboard.html", context=page_context(request, stats=crud.get_statistics(db), tasks=tasks, active_page="dashboard"))


@router.get("/tasks", response_class=HTMLResponse, name="tasks")
def tasks_page(
    request: Request,
    search: str = "",
    status_filter: str = "",
    priority: str = "",
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    tasks = crud.get_tasks(db, search=search.strip(), status=status_filter, priority=priority, sort=sort)
    return templates.TemplateResponse(request=request, name="tasks.html", context=page_context(request, tasks=tasks, stats=crud.get_statistics(db), search=search, status_filter=status_filter, priority=priority, sort=sort, active_page="tasks"))


@router.get("/tasks/new", response_class=HTMLResponse, name="create_task_page")
def create_task_page(request: Request):
    return templates.TemplateResponse(request=request, name="create_task.html", context=page_context(request, active_page="create", error=None))


@router.post("/tasks", name="create_task")
async def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    task_status: str = Form("Pending"),
    due_date: str = Form(""),
    attachment: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        data = TaskCreate(title=title.strip(), description=description.strip() or None, priority=priority, status=task_status, due_date=due_date or None)
        filename = await save_upload(attachment)
        crud.create_task(db, data, filename)
    except (ValueError, Exception) as exc:
        if isinstance(exc, HTTPException):
            raise
        return templates.TemplateResponse(request=request, name="create_task.html", context=page_context(request, active_page="create", error=str(exc)), status_code=400)
    return RedirectResponse("/tasks?message=Task+created+successfully", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse, name="edit_task_page")
def edit_task_page(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse(request=request, name="edit_task.html", context=page_context(request, task=task, active_page="tasks", error=None))


@router.post("/tasks/{task_id}/edit", name="update_task")
async def update_task(
    task_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    task_status: str = Form("Pending"),
    due_date: str = Form(""),
    attachment: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        data = TaskUpdate(title=title.strip(), description=description.strip() or None, priority=priority, status=task_status, due_date=due_date or None)
        filename = await save_upload(attachment)
        crud.update_task(db, task, data, filename)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="edit_task.html", context=page_context(request, task=task, active_page="tasks", error=str(exc)), status_code=400)
    return RedirectResponse("/tasks?message=Task+updated+successfully", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/toggle", name="toggle_task")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.toggle_task_status(db, task)
    return RedirectResponse("/tasks?message=Task+status+updated", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/delete", name="delete_task")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.attachment:
        (UPLOAD_DIR / task.attachment).unlink(missing_ok=True)
    crud.delete_task(db, task)
    return RedirectResponse("/tasks?message=Task+deleted", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/uploads/{filename}", name="uploaded_file")
def uploaded_file(filename: str):
    safe_path = (UPLOAD_DIR / Path(filename).name).resolve()
    if safe_path.parent != UPLOAD_DIR.resolve() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="Attachment not found")
    return FileResponse(safe_path)
