import argparse
import sys

from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import load_data, save_data
from utils.display import (
    console, success, error, warn, info,
    print_users, print_projects, print_tasks, print_project_detail,
)
from utils.validators import validate_email, validate_date, validate_status


# ══════════════════════════════════════════════════════════════════════════════
# Handler functions
# ══════════════════════════════════════════════════════════════════════════════

def cmd_add_user(args):
    """Create a new user and persist to disk."""
    try:
        email = validate_email(args.email)
    except ValueError as exc:
        error(str(exc))
        return 1

    if User.find_by_email(email):
        error(f"A user with email '{email}' already exists.")
        return 1
    if User.find_by_name(args.name):
        warn(f"A user named '{args.name}' already exists — adding anyway (use email to distinguish).")

    user = User(name=args.name, email=email)
    User.register(user)
    save_data()
    success(f"User created: {user}")
    return 0


def cmd_list_users(_args):
    """Display all users."""
    print_users(User.all_users)
    return 0


def cmd_delete_user(args):
    """Remove a user (and all their projects) by name."""
    user = User.find_by_name(args.name)
    if not user:
        error(f"No user found with name '{args.name}'.")
        return 1
    User.all_users.remove(user)
    save_data()
    success(f"Deleted user '{user.name}' and all their projects.")
    return 0


def cmd_add_project(args):
    """Add a project to a user."""
    user = User.find_by_name(args.user)
    if not user:
        error(f"No user found with name '{args.user}'. Create them first.")
        return 1

    if user.get_project_by_title(args.title):
        error(f"User '{args.user}' already has a project titled '{args.title}'.")
        return 1

    due_date = ""
    if args.due_date:
        try:
            due_date = validate_date(args.due_date)
        except ValueError as exc:
            error(str(exc))
            return 1

    project = Project(
        title=args.title,
        description=args.description or "",
        due_date=due_date,
        owner=user.name,
    )
    user.add_project(project)
    save_data()
    success(f"Project created: {project}")
    return 0


def cmd_list_projects(args):
    """List all projects, or only those belonging to a user."""
    if args.user:
        user = User.find_by_name(args.user)
        if not user:
            error(f"No user found with name '{args.user}'.")
            return 1
        print_projects(user.projects, heading=f"{user.name}'s Projects")
    else:
        all_projects = [p for u in User.all_users for p in u.projects]
        print_projects(all_projects, heading="All Projects")
    return 0


def cmd_show_project(args):
    """Show full detail of a single project by title."""
    project = _find_project_by_title(args.title)
    if not project:
        error(f"No project found with title '{args.title}'.")
        return 1
    print_project_detail(project)
    return 0


def cmd_delete_project(args):
    """Delete a project by title."""
    for user in User.all_users:
        project = user.get_project_by_title(args.title)
        if project:
            user._projects.remove(project)
            save_data()
            success(f"Deleted project '{project.title}' from user '{user.name}'.")
            return 0
    error(f"No project found with title '{args.title}'.")
    return 1


def cmd_search_projects(args):
    """Search projects by keyword in title or description."""
    query = args.query.lower()
    results = []
    for user in User.all_users:
        for p in user.projects:
            if query in p.title.lower() or query in p.description.lower():
                results.append(p)
    if results:
        print_projects(results, heading=f"Search results for '{args.query}'")
    else:
        warn(f"No projects matched '{args.query}'.")
    return 0


def cmd_add_task(args):
    """Add a task to a project."""
    project = _find_project_by_title(args.project)
    if not project:
        error(f"No project found with title '{args.project}'.")
        return 1

    if project.get_task_by_title(args.title):
        error(f"Task '{args.title}' already exists in project '{args.project}'.")
        return 1

    task = Task(
        title=args.title,
        assigned_to=args.assign or "Unassigned",
    )
    project.add_task(task)
    save_data()
    success(f"Task added: {task}")
    return 0


def cmd_list_tasks(args):
    """List all tasks in a project."""
    project = _find_project_by_title(args.project)
    if not project:
        error(f"No project found with title '{args.project}'.")
        return 1
    print_tasks(project.tasks, project_title=project.title)
    return 0


def cmd_complete_task(args):
    """Mark a task as complete."""
    project = _find_project_by_title(args.project)
    if not project:
        error(f"No project found with title '{args.project}'.")
        return 1
    task = project.get_task_by_id(args.task_id)
    if not task:
        error(f"No task with ID {args.task_id} in project '{args.project}'.")
        return 1
    task.status = "complete"
    save_data()
    success(f"Task #{task.id} '{task.title}' marked as complete.")
    return 0


def cmd_update_task(args):
    """Update a task's status or assignment."""
    project = _find_project_by_title(args.project)
    if not project:
        error(f"No project found with title '{args.project}'.")
        return 1
    task = project.get_task_by_id(args.task_id)
    if not task:
        error(f"No task with ID {args.task_id} in project '{args.project}'.")
        return 1

    changed = False
    if args.status:
        try:
            task.status = validate_status(args.status)
            changed = True
        except ValueError as exc:
            error(str(exc))
            return 1
    if args.assign:
        task.assigned_to = args.assign
        changed = True
    if args.title:
        task.title = args.title
        changed = True

    if changed:
        save_data()
        success(f"Task #{task.id} updated: {task}")
    else:
        warn("Nothing to update — provide --status, --assign, or --title.")
    return 0


def cmd_summary(_args):
    """Print a summary of the whole tracker."""
    total_users = len(User.all_users)
    total_projects = sum(len(u.projects) for u in User.all_users)
    total_tasks = sum(len(p.tasks) for u in User.all_users for p in u.projects)
    done_tasks = sum(
        len(p.complete_tasks()) for u in User.all_users for p in u.projects
    )
    info(
        f"[bold]Tracker Summary:[/bold]  "
        f"{total_users} user(s)  |  "
        f"{total_projects} project(s)  |  "
        f"{total_tasks} task(s) total  |  "
        f"{done_tasks} complete"
    )
    return 0


# ══════════════════════════════════════════════════════════════════════════════
# Private helpers
# ══════════════════════════════════════════════════════════════════════════════

def _find_project_by_title(title: str) -> Project | None:
    """Search all users' projects for one matching the given title."""
    title_lower = title.lower()
    for user in User.all_users:
        for project in user.projects:
            if project.title.lower() == title_lower:
                return project
    return None


# ══════════════════════════════════════════════════════════════════════════════
# CLI parser setup
# ══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="[bold cyan]Project Tracker CLI[/bold cyan] — manage users, projects, and tasks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py add-user --name 'Alex' --email 'alex@dev.io'\n"
            "  python main.py add-project --user 'Alex' --title 'CLI Tool' --due-date '2025-12-31'\n"
            "  python main.py add-task --project 'CLI Tool' --title 'Write tests' --assign 'Alex'\n"
            "  python main.py complete-task --project 'CLI Tool' --task-id 1\n"
            "  python main.py search-projects --query 'CLI'\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ── user commands ──────────────────────────────────────────────────────────
    p = sub.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True, help="User's full name")
    p.add_argument("--email", required=True, help="User's email address")
    p.set_defaults(func=cmd_add_user)

    p = sub.add_parser("list-users", help="List all users")
    p.set_defaults(func=cmd_list_users)

    p = sub.add_parser("delete-user", help="Delete a user and all their projects")
    p.add_argument("--name", required=True, help="Name of user to delete")
    p.set_defaults(func=cmd_delete_user)

    # ── project commands ───────────────────────────────────────────────────────
    p = sub.add_parser("add-project", help="Add a project to a user")
    p.add_argument("--user", required=True, help="Owner's name")
    p.add_argument("--title", required=True, help="Project title")
    p.add_argument("--description", default="", help="Short project description")
    p.add_argument("--due-date", dest="due_date", default="", help="Due date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_add_project)

    p = sub.add_parser("list-projects", help="List projects (all, or filtered by user)")
    p.add_argument("--user", default="", help="Filter by user name")
    p.set_defaults(func=cmd_list_projects)

    p = sub.add_parser("show-project", help="Show full details of a project")
    p.add_argument("--title", required=True, help="Project title")
    p.set_defaults(func=cmd_show_project)

    p = sub.add_parser("delete-project", help="Delete a project")
    p.add_argument("--title", required=True, help="Project title to delete")
    p.set_defaults(func=cmd_delete_project)

    p = sub.add_parser("search-projects", help="Search projects by keyword")
    p.add_argument("--query", required=True, help="Keyword to search in title/description")
    p.set_defaults(func=cmd_search_projects)

    # ── task commands ──────────────────────────────────────────────────────────
    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True, help="Project title")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--assign", default="", help="Name of person assigned to this task")
    p.set_defaults(func=cmd_add_task)

    p = sub.add_parser("list-tasks", help="List all tasks in a project")
    p.add_argument("--project", required=True, help="Project title")
    p.set_defaults(func=cmd_list_tasks)

    p = sub.add_parser("complete-task", help="Mark a task as complete")
    p.add_argument("--project", required=True, help="Project title")
    p.add_argument("--task-id", dest="task_id", required=True, type=int, help="Task ID")
    p.set_defaults(func=cmd_complete_task)

    p = sub.add_parser("update-task", help="Update a task's title, status, or assignee")
    p.add_argument("--project", required=True, help="Project title")
    p.add_argument("--task-id", dest="task_id", required=True, type=int, help="Task ID")
    p.add_argument("--status", default="", help="New status: pending | in_progress | complete")
    p.add_argument("--assign", default="", help="Re-assign task to this person")
    p.add_argument("--title", default="", help="New task title")
    p.set_defaults(func=cmd_update_task)

    # ── summary ────────────────────────────────────────────────────────────────
    p = sub.add_parser("summary", help="Show a quick overview of the tracker")
    p.set_defaults(func=cmd_summary)

    return parser


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Load persisted data first
    try:
        load_data()
    except RuntimeError as exc:
        error(str(exc))
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    exit_code = args.func(args)
    sys.exit(exit_code or 0)


if __name__ == "__main__":
    main()
