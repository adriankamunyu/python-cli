from datetime import datetime
from models.task import Task

class Project:
    _id_counter: int = 1

    def __init__(self, title: str, description: str = "",
                 due_date: str = None, owner: str = "",
                 project_id: int = None, created_at: str = None):
        self._id = project_id if project_id is not None else Project._id_counter
        if project_id is None:
            Project._id_counter += 1

        self._title = title
        self._description = description
        self._due_date = due_date or ""
        self._owner = owner
        self._tasks: list[Task] = []
        self._created_at = created_at or datetime.now().isoformat()

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value or not value.strip():
            raise ValueError("Project title cannot be empty.")
        self._title = value.strip()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def due_date(self) -> str:
        return self._due_date

    @due_date.setter
    def due_date(self, value: str):
        self._due_date = value

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks)

    @property
    def created_at(self) -> str:
        return self._created_at


    def add_task(self, task: Task):
        self._tasks.append(task)

    def get_task_by_id(self, task_id: int) -> Task | None:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    def get_task_by_title(self, title: str) -> Task | None:
        title_lower = title.lower()
        for t in self._tasks:
            if t.title.lower() == title_lower:
                return t
        return None

    def pending_tasks(self) -> list[Task]:
        return [t for t in self._tasks if t.status != "complete"]

    def complete_tasks(self) -> list[Task]:
        return [t for t in self._tasks if t.status == "complete"]


    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "owner": self._owner,
            "created_at": self._created_at,
            "tasks": [t.to_dict() for t in self._tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        project = cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            owner=data.get("owner", ""),
            project_id=data.get("id"),
            created_at=data.get("created_at"),
        )
        if project._id >= cls._id_counter:
            cls._id_counter = project._id + 1
        for task_data in data.get("tasks", []):
            project.add_task(Task.from_dict(task_data))
        return project


    def __str__(self) -> str:
        due = f" | Due: {self._due_date}" if self._due_date else ""
        return (
            f"[{self._id}] {self._title} (owner: {self._owner}){due} "
            f"| Tasks: {len(self._tasks)}"
        )

    def __repr__(self) -> str:
        return (
            f"Project(id={self._id}, title={self._title!r}, "
            f"owner={self._owner!r}, tasks={len(self._tasks)})"
        )
