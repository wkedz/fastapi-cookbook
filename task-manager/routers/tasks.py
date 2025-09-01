from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from models import Task, TaskWithId
from operations import read_all_tasks, read_task, create_task, modify_task, remove_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

class UpdateTask(BaseModel):
    """
    Model for updating a task.
    """
    title: str | None = None
    description: str | None = None
    status: str | None = None
    

@router.get("/", response_model=list[TaskWithId])
def get_tasks():
    """
    Retrieve all tasks.
    """
    return read_all_tasks()

@router.get("/{task_id}", response_model=TaskWithId)
def get_task(task_id: int):
    """
    Retrieve a specific task by its ID.
    """
    task = read_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.post("/", response_model=TaskWithId, status_code=status.HTTP_201_CREATED)
def add_task(task: Task):
    """
    Create a new task.
    """
    return create_task(task)

@router.put("/{task_id}", response_model=TaskWithId)
def update_task(task_id: int, task_update: UpdateTask):
    """
    Update an existing task by its ID.
    """
    modified = modify_task(task_id, task_update.model_dump(exclude_unset=True))
    if modified is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return modified

@router.delete("/{task_id}", response_model=Task)
def delete_task(task_id: int):
    removed_task = remove_task(task_id)
    if not removed_task:
        raise HTTPException(
            status_code=404, detail="task not found"
        )
    return removed_task