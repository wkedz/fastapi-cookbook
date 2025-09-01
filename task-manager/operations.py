import csv

from models import Task, TaskWithId

DATABASE_FILENAME = "tasks.csv"

column_fields = [
    "id", "title", "description", "status"
]

def read_all_tasks() -> list[TaskWithId]:
    with open(DATABASE_FILENAME) as csvfile:
        reader = csv.DictReader(csvfile)
        return [TaskWithId(id=int(row["id"]), title=row["title"], description=row["description"], status=row["status"]) for row in reader]

def read_task(task_id : int) -> TaskWithId | None:
    tasks = read_all_tasks()
    for task in tasks:
        if task.id == task_id:
            return task
    return None

def save_task(task: TaskWithId) -> None:
    with open(DATABASE_FILENAME, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_fields)
        writer.writerow(task.model_dump())

def create_task(task: Task) -> TaskWithId:
    task_id = get_next_id()
    task_with_id = TaskWithId(id=task_id, **task.model_dump())
    save_task(task_with_id)
    return task_with_id

def modify_task(id: int, task: dict) -> TaskWithId | None: # type: ignore
    updated_task: TaskWithId | None = None
    tasks : list[TaskWithId] = read_all_tasks()
    for number, task_ in enumerate(tasks):
        if task_.id == id:
            tasks[number] = (
                updated_task
            ) = task_.model_copy(update=task)
    with open(
        DATABASE_FILENAME, mode="w", newline=""
    ) as csvfile: # rewrite the file
        writer = csv.DictWriter(
            csvfile,
            fieldnames=column_fields,
        )
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.model_dump())
    if updated_task:
        return updated_task
    return None

def remove_task(id: int) -> Task | None:
    deleted_task: Task | None = None
    tasks = read_all_tasks()
    with open(
        DATABASE_FILENAME, mode="w", newline=""
    ) as csvfile:  # rewrite the file
        writer = csv.DictWriter(
            csvfile,
            fieldnames=column_fields,
        )
        writer.writeheader()
        for task in tasks:
            if task.id == id:
                deleted_task = task
                continue
            writer.writerow(task.model_dump())
    if deleted_task:
        dict_task_without_id = deleted_task.model_dump()
        del dict_task_without_id["id"]
        return Task(**dict_task_without_id)
    return None

def get_next_id() -> int:
    try:
        tasks = read_all_tasks()
        if not tasks:
            return 1
        return max(task.id for task in tasks) + 1
    except (FileNotFoundError, ValueError):
        return 1