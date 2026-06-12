from models.person import Person
from models.project import Project


class User(Person):
    """A system user who owns projects. Inherits from Person."""

    _id_counter: int = 1
    all_users: list["User"] = []  # class-level registry

    def __init__(self, name: str, email: str, user_id: int = None):
        super().__init__(name, email)
        self._id = user_id if user_id is not None else User._id_counter
        if user_id is None:
            User._id_counter += 1
        self._projects: list[Project] = []

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def id(self) -> int:
        return self._id

    @property
    def projects(self) -> list[Project]:
        return list(self._projects)

    # ── project management ────────────────────────────────────────────────────

    def add_project(self, project: Project):
        self._projects.append(project)

    def get_project_by_title(self, title: str) -> Project | None:
        title_lower = title.lower()
        for p in self._projects:
            if p.title.lower() == title_lower:
                return p
        return None

    def get_project_by_id(self, project_id: int) -> Project | None:
        for p in self._projects:
            if p.id == project_id:
                return p
        return None

    # ── class methods ─────────────────────────────────────────────────────────

    @classmethod
    def find_by_name(cls, name: str) -> "User | None":
        name_lower = name.lower()
        for u in cls.all_users:
            if u.name.lower() == name_lower:
                return u
        return None

    @classmethod
    def find_by_email(cls, email: str) -> "User | None":
        email_lower = email.lower()
        for u in cls.all_users:
            if u.email.lower() == email_lower:
                return u
        return None

    @classmethod
    def register(cls, user: "User"):
        """Add a user to the global registry."""
        cls.all_users.append(user)

    @classmethod
    def clear_registry(cls):
        cls.all_users.clear()
        cls._id_counter = 1

    # ── serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "projects": [p.to_dict() for p in self._projects],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(
            name=data["name"],
            email=data["email"],
            user_id=data.get("id"),
        )
        if user._id >= cls._id_counter:
            cls._id_counter = user._id + 1
        for project_data in data.get("projects", []):
            user.add_project(Project.from_dict(project_data))
        return user

    # ── display ───────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"[{self._id}] {self._name} <{self._email}> "
            f"| Projects: {len(self._projects)}"
        )

    def __repr__(self) -> str:
        return (
            f"User(id={self._id}, name={self._name!r}, "
            f"email={self._email!r}, projects={len(self._projects)})"
        )
