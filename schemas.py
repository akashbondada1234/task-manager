from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High)$")
    status: str = Field(default="Pending", pattern="^(Pending|Completed)$")
    due_date: date | None = None


class TaskUpdate(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
