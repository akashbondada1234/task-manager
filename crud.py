from datetime import date, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from models import Task
from schemas import TaskCreate, TaskUpdate


def create_task(db: Session, task_data: TaskCreate, attachment: str | None = None) -> Task:
    task = Task(**task_data.model_dump(), attachment=attachment)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(
    db: Session,
    search: str = "",
    status: str = "",
    priority: str = "",
    sort: str = "newest",
) -> list[Task]:
    query: Select[tuple[Task]] = select(Task)
    if search:
        query = query.where(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))
    if status in {"Pending", "Completed"}:
        query = query.where(Task.status == status)
    if priority in {"Low", "Medium", "High"}:
        query = query.where(Task.priority == priority)
    if sort == "oldest":
        query = query.order_by(Task.created_at.asc())
    elif sort == "due_soon":
        query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    else:
        query = query.order_by(Task.created_at.desc())
    return list(db.scalars(query).all())


def update_task(db: Session, task: Task, task_data: TaskUpdate, attachment: str | None = None) -> Task:
    for key, value in task_data.model_dump().items():
        setattr(task, key, value)
    if attachment is not None:
        task.attachment = attachment
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def toggle_task_status(db: Session, task: Task) -> Task:
    task.status = "Completed" if task.status == "Pending" else "Pending"
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def get_statistics(db: Session) -> dict[str, int | float]:
    total = db.scalar(select(func.count(Task.id))) or 0
    completed = db.scalar(select(func.count(Task.id)).where(Task.status == "Completed")) or 0
    pending = total - completed
    percentage = round((completed / total) * 100) if total else 0
    return {"total": total, "pending": pending, "completed": completed, "percentage": percentage}
