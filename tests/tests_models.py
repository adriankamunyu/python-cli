import os
import json
import pytest
import sys

# Make sure the project root is on the path when running from any directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.task import Task
from models.project import Project
from models.user import User
from utils.validators import validate_email, validate_date, validate_status


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def reset_registries():
    """Reset all class-level state before every test."""
    User.clear_registry()
    Project._id_counter = 1
    Task._id_counter = 1
    yield
    User.clear_registry()
    Project._id_counter = 1
    Task._id_counter = 1


# ══════════════════════════════════════════════════════════════════════════════
# Task tests
# ══════════════════════════════════════════════════════════════════════════════

class TestTask:
    def test_create_task_defaults(self):
        t = Task("Write docs")
        assert t.title == "Write docs"
        assert t.status == "pending"
        assert t.assigned_to == "Unassigned"

    def test_task_id_auto_increments(self):
        t1 = Task("Task 1")
        t2 = Task("Task 2")
        assert t2.id == t1.id + 1

    def test_status_setter_valid(self):
        t = Task("Test")
        t.status = "in_progress"
        assert t.status == "in_progress"
        t.status = "complete"
        assert t.status == "complete"

    def test_status_setter_invalid(self):
        t = Task("Test")
        with pytest.raises(ValueError):
            t.status = "done"

    def test_title_setter_empty_raises(self):
        t = Task("Test")
        with pytest.raises(ValueError):
            t.title = ""

    def test_to_dict_and_from_dict(self):
        t = Task("Implement feature", assigned_to="Alex", status="in_progress")
        d = t.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == t.id
        assert restored.title == t.title
        assert restored.status == t.status
        assert restored.assigned_to == t.assigned_to

    def test_str_representation(self):
        t = Task("My task")
        assert "My task" in str(t)
        assert "pending" in str(t)


# ══════════════════════════════════════════════════════════════════════════════
# Project tests
# ══════════════════════════════════════════════════════════════════════════════

class TestProject:
    def test_create_project(self):
        p = Project("API Redesign", description="REST to GraphQL", owner="Sam")
        assert p.title == "API Redesign"
        assert p.owner == "Sam"
        assert p.tasks == []

    def test_add_task(self):
        p = Project("Proj")
        t = Task("Task A")
        p.add_task(t)
        assert len(p.tasks) == 1

    def test_get_task_by_id(self):
        p = Project("Proj")
        t = Task("Find me")
        p.add_task(t)
        found = p.get_task_by_id(t.id)
        assert found is t

    def test_get_task_by_title_case_insensitive(self):
        p = Project("Proj")
        t = Task("Deploy App")
        p.add_task(t)
        assert p.get_task_by_title("deploy app") is t

    def test_pending_and_complete_tasks(self):
        p = Project("Proj")
        t1 = Task("T1")
        t2 = Task("T2")
        t2.status = "complete"
        p.add_task(t1)
        p.add_task(t2)
        assert len(p.pending_tasks()) == 1
        assert len(p.complete_tasks()) == 1

    def test_serialisation_roundtrip(self):
        p = Project("Test Project", description="desc", due_date="2025-06-01", owner="Dev")
        p.add_task(Task("Task 1", assigned_to="Dev"))
        d = p.to_dict()
        restored = Project.from_dict(d)
        assert restored.title == p.title
        assert restored.owner == p.owner
        assert len(restored.tasks) == 1

    def test_title_setter_empty_raises(self):
        p = Project("Proj")
        with pytest.raises(ValueError):
            p.title = "  "


# ══════════════════════════════════════════════════════════════════════════════
# User tests
# ══════════════════════════════════════════════════════════════════════════════

class TestUser:
    def test_create_user(self):
        u = User("Alex", "alex@dev.io")
        assert u.name == "Alex"
        assert u.email == "alex@dev.io"

    def test_invalid_email_raises(self):
        from models.person import Person
        p = Person("Test", "valid@email.com")
        with pytest.raises(ValueError):
            p.email = "not-an-email"

    def test_add_and_find_project(self):
        u = User("Sam", "sam@dev.io")
        p = Project("Alpha", owner="Sam")
        u.add_project(p)
        assert u.get_project_by_title("alpha") is p

    def test_find_by_name_classmethod(self):
        u = User("Jordan", "j@dev.io")
        User.register(u)
        found = User.find_by_name("jordan")
        assert found is u

    def test_find_by_email_classmethod(self):
        u = User("Casey", "casey@dev.io")
        User.register(u)
        found = User.find_by_email("CASEY@DEV.IO")
        assert found is u

    def test_find_by_name_not_found(self):
        assert User.find_by_name("nobody") is None

    def test_user_id_increments(self):
        u1 = User("A", "a@x.com")
        u2 = User("B", "b@x.com")
        assert u2.id == u1.id + 1

    def test_serialisation_roundtrip(self):
        u = User("Riley", "riley@dev.io")
        p = Project("Project X", owner="Riley")
        p.add_task(Task("Task 1"))
        u.add_project(p)
        d = u.to_dict()
        restored = User.from_dict(d)
        assert restored.name == u.name
        assert restored.email == u.email
        assert len(restored.projects) == 1
        assert len(restored.projects[0].tasks) == 1


# ══════════════════════════════════════════════════════════════════════════════
# Validator tests
# ══════════════════════════════════════════════════════════════════════════════

class TestValidators:
    def test_validate_email_valid(self):
        assert validate_email("User@Example.COM") == "user@example.com"

    def test_validate_email_invalid(self):
        for bad in ["notanemail", "missing@dot", "@nodomain.com"]:
            with pytest.raises(ValueError):
                validate_email(bad)

    def test_validate_date_iso(self):
        assert validate_date("2025-12-31") == "2025-12-31"

    def test_validate_date_natural(self):
        result = validate_date("December 31 2025")
        assert result == "2025-12-31"

    def test_validate_date_invalid(self):
        with pytest.raises(ValueError):
            validate_date("not-a-date")

    def test_validate_status_valid(self):
        assert validate_status("COMPLETE") == "complete"
        assert validate_status("in_progress") == "in_progress"

    def test_validate_status_invalid(self):
        with pytest.raises(ValueError):
            validate_status("done")


# ══════════════════════════════════════════════════════════════════════════════
# Storage tests
# ══════════════════════════════════════════════════════════════════════════════

class TestStorage:
    def test_save_and_load(self, tmp_path, monkeypatch):
        """Data saved to disk should reload correctly."""
        import utils.storage as storage_mod
        monkeypatch.setattr(storage_mod, "DATA_FILE", str(tmp_path / "test_data.json"))
        monkeypatch.setattr(storage_mod, "DATA_DIR", str(tmp_path))

        u = User("Morgan", "morgan@dev.io")
        p = Project("Load Test", owner="Morgan")
        p.add_task(Task("Persist me"))
        u.add_project(p)
        User.register(u)

        storage_mod.save_data()
        storage_mod.load_data()

        assert len(User.all_users) == 1
        loaded_user = User.all_users[0]
        assert loaded_user.name == "Morgan"
        assert len(loaded_user.projects) == 1
        assert len(loaded_user.projects[0].tasks) == 1

    def test_load_missing_file_is_safe(self, tmp_path, monkeypatch):
        """Loading when no file exists should not raise."""
        import utils.storage as storage_mod
        monkeypatch.setattr(
            storage_mod, "DATA_FILE", str(tmp_path / "nonexistent.json")
        )
        storage_mod.load_data()  # should not raise

    def test_load_corrupt_file_raises(self, tmp_path, monkeypatch):
        """A malformed JSON file should raise RuntimeError."""
        import utils.storage as storage_mod
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json{{")
        monkeypatch.setattr(storage_mod, "DATA_FILE", str(bad_file))
        with pytest.raises(RuntimeError):
            storage_mod.load_data()
