from datetime import datetime


class Task:
    """Represents a single task inside a project."""

    _id_counter: int = 1

    def __init__(self, title: str, assigned_to: str = "Unassigned",
                 status: str = "pending", task_id: int = None,
                 created_at: str = None):
        self._id = task_id if task_id is not None else Task._id_counter
        if task_id is None:
            Task._id_counter += 1

        self._title = title
        self._assigned_to = assigned_to
        self._status = status  # "pending" | "in_progress" | "complete"
        self._created_at = created_at or datetime.now().isoformat()

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty.")
        self._title = value.strip()

    @property
    def assigned_to(self) -> str:
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value: str):
        self._assigned_to = value.strip()

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        allowed = {"pending", "in_progress", "complete"}
        if value not in allowed:
            raise ValueError(f"Status must be one of {allowed}, got {value!r}.")
        self._status = value

    @property
    def created_at(self) -> str:
        return self._created_at

    # ── serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "title": self._title,
            "assigned_to": self._assigned_to,
            "status": self._status,
            "created_at": self._created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            title=data["title"],
            assigned_to=data.get("assigned_to", "Unassigned"),
            status=data.get("status", "pending"),
            task_id=data.get("id"),
            created_at=data.get("created_at"),
        )
        # Keep the global counter ahead of any loaded IDs
        if task._id >= cls._id_counter:
            cls._id_counter = task._id + 1
        return task

    # ── display ───────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"[{self._id}] {self._title} | "
            f"Assigned: {self._assigned_to} | Status: {self._status}"
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self._id}, title={self._title!r}, "
            f"status={self._status!r})"
        )
