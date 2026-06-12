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


def cmd_add_user(args=None):
    name  = args.name  if args else input("  Name  : ").strip()
    email = args.email if args else input("  Email : ").strip()
    try:
        email = validate_email(email)
    except ValueError as exc:
        error(str(exc))
        return 1
    if User.find_by_email(email):
        error(f"A user with email '{email}' already exists.")
        return 1
    if User.find_by_name(name):
        warn(f"A user named '{name}' already exists — adding anyway.")
    user = User(name=name, email=email)
    User.register(user)
    save_data()
    success(f"User created: {user}")
    return 0


def cmd_list_users(_args=None):
    print_users(User.all_users)
    return 0


def cmd_view_user_details(_args=None):
    name = input("  User name: ").strip()
    user = User.find_by_name(name)
    if not user:
        error(f"No user found with name '{name}'.")
        return 1
    console.print(f"\n[bold]Name:[/bold]     {user.name}")
    console.print(f"[bold]Email:[/bold]    {user.email}")
    console.print(f"[bold]Projects:[/bold] {len(user.projects)}")
    print_projects(user.projects, heading=f"{user.name}'s Projects")
    return 0


def cmd_delete_user(args=None):
    name = args.name if args else input("  User name to remove: ").strip()
    user = User.find_by_name(name)
    if not user:
        error(f"No user found with name '{name}'.")
        return 1
    User.all_users.remove(user)
    save_data()
    success(f"Deleted user '{user.name}' and all their projects.")
    return 0


def cmd_add_project(args=None):
    if args:
        user_name, title, description, due_date_raw = (
            args.user, args.title, args.description or "", args.due_date or ""
        )
    else:
        user_name     = input("  Owner (user name)        : ").strip()
        title         = input("  Project title            : ").strip()
        description   = input("  Description              : ").strip()
        due_date_raw  = input("  Due date (YYYY-MM-DD, or blank): ").strip()

    user = User.find_by_name(user_name)
    if not user:
        error(f"No user found with name '{user_name}'.")
        return 1
    if user.get_project_by_title(title):
        error(f"'{user_name}' already has a project titled '{title}'.")
        return 1

    due_date = ""
    if due_date_raw:
        try:
            due_date = validate_date(due_date_raw)
        except ValueError as exc:
            error(str(exc))
            return 1

    project = Project(title=title, description=description,
                      due_date=due_date, owner=user.name)
    user.add_project(project)
    save_data()
    success(f"Project created: {project}")
    return 0


def cmd_list_projects(args=None):
    user_name = (args.user if args else "") or ""
    if user_name:
        user = User.find_by_name(user_name)
        if not user:
            error(f"No user found with name '{user_name}'.")
            return 1
        print_projects(user.projects, heading=f"{user.name}'s Projects")
    else:
        all_projects = [p for u in User.all_users for p in u.projects]
        print_projects(all_projects, heading="All Projects")
    return 0


def cmd_show_project(args=None):
    title = args.title if args else input("  Project title: ").strip()
    project = _find_project_by_title(title)
    if not project:
        error(f"No project found with title '{title}'.")
        return 1
    print_project_detail(project)
    return 0


def cmd_delete_project(args=None):
    title = args.title if args else input("  Project title to delete: ").strip()
    for user in User.all_users:
        project = user.get_project_by_title(title)
        if project:
            user._projects.remove(project)
            save_data()
            success(f"Deleted project '{project.title}' from user '{user.name}'.")
            return 0
    error(f"No project found with title '{title}'.")
    return 1


def cmd_search_projects(args=None):
    query = args.query if args else input("  Search keyword: ").strip()
    q = query.lower()
    results = [
        p for u in User.all_users for p in u.projects
        if q in p.title.lower() or q in p.description.lower()
    ]
    if results:
        print_projects(results, heading=f"Results for '{query}'")
    else:
        warn(f"No projects matched '{query}'.")
    return 0


def cmd_add_task(args=None):
    if args:
        project_title, title, assign = args.project, args.title, args.assign or ""
    else:
        project_title = input("  Project title : ").strip()
        title         = input("  Task title    : ").strip()
        assign        = input("  Assign to     : ").strip()

    project = _find_project_by_title(project_title)
    if not project:
        error(f"No project found with title '{project_title}'.")
        return 1
    if project.get_task_by_title(title):
        error(f"Task '{title}' already exists in '{project_title}'.")
        return 1

    task = Task(title=title, assigned_to=assign or "Unassigned")
    project.add_task(task)
    save_data()
    success(f"Task added: {task}")
    return 0


def cmd_list_tasks(args=None):
    project_title = args.project if args else input("  Project title: ").strip()
    project = _find_project_by_title(project_title)
    if not project:
        error(f"No project found with title '{project_title}'.")
        return 1
    print_tasks(project.tasks, project_title=project.title)
    return 0


def cmd_complete_task(args=None):
    if args:
        project_title, task_id = args.project, args.task_id
    else:
        project_title = input("  Project title : ").strip()
        try:
            task_id = int(input("  Task ID       : ").strip())
        except ValueError:
            error("Task ID must be a number.")
            return 1

    project = _find_project_by_title(project_title)
    if not project:
        error(f"No project found with title '{project_title}'.")
        return 1
    task = project.get_task_by_id(task_id)
    if not task:
        error(f"No task with ID {task_id} in '{project_title}'.")
        return 1
    task.status = "complete"
    save_data()
    success(f"Task #{task.id} '{task.title}' marked as complete.")
    return 0


def cmd_update_task(args=None):
    if args:
        project_title = args.project
        task_id       = args.task_id
        new_status    = args.status
        new_assign    = args.assign
        new_title     = args.title
    else:
        project_title = input("  Project title          : ").strip()
        try:
            task_id = int(input("  Task ID                : ").strip())
        except ValueError:
            error("Task ID must be a number.")
            return 1
        new_status = input("  New status (or blank)  : ").strip()
        new_assign = input("  Re-assign to (or blank): ").strip()
        new_title  = input("  New title (or blank)   : ").strip()

    project = _find_project_by_title(project_title)
    if not project:
        error(f"No project found with title '{project_title}'.")
        return 1
    task = project.get_task_by_id(task_id)
    if not task:
        error(f"No task with ID {task_id} in '{project_title}'.")
        return 1

    changed = False
    if new_status:
        try:
            task.status = validate_status(new_status)
            changed = True
        except ValueError as exc:
            error(str(exc))
            return 1
    if new_assign:
        task.assigned_to = new_assign
        changed = True
    if new_title:
        task.title = new_title
        changed = True

    if changed:
        save_data()
        success(f"Task #{task.id} updated: {task}")
    else:
        warn("Nothing to update.")
    return 0


def cmd_summary(_args=None):
    total_users    = len(User.all_users)
    total_projects = sum(len(u.projects) for u in User.all_users)
    total_tasks    = sum(len(p.tasks) for u in User.all_users for p in u.projects)
    done_tasks     = sum(len(p.complete_tasks()) for u in User.all_users for p in u.projects)
    info(
        f"[bold]Tracker Summary:[/bold]  "
        f"{total_users} user(s)  |  {total_projects} project(s)  |  "
        f"{total_tasks} task(s) total  |  {done_tasks} complete"
    )
    return 0


MENU = """
 PROJECT MANAGEMENT SYSTEM

  MAIN MENU

  USER MANAGEMENT
    1.  Add User
    2.  List All Users
    3.  View User Details
    4.  Remove User

  PROJECT MANAGEMENT
    5.  Add Project
    6.  List All Projects
    7.  View Project Details
    8.  Delete Project
    9.  Search Projects

  TASK MANAGEMENT
    10. Add Task
    11. List Tasks
    12. Complete Task
    13. Update Task

  OTHER
    14. Summary
     0. Exit

  """

MENU_ACTIONS = {
    "1":  cmd_add_user,
    "2":  cmd_list_users,
    "3":  cmd_view_user_details,
    "4":  cmd_delete_user,
    "5":  cmd_add_project,
    "6":  cmd_list_projects,
    "7":  cmd_show_project,
    "8":  cmd_delete_project,
    "9":  cmd_search_projects,
    "10": cmd_add_task,
    "11": cmd_list_tasks,
    "12": cmd_complete_task,
    "13": cmd_update_task,
    "14": cmd_summary,
}


def run_interactive_menu():
    while True:
        print(MENU)
        choice = input("  Enter option: ").strip()
        print()
        if choice == "0":
            console.print("\n  [bold cyan]Goodbye![/bold cyan]\n")
            break
        action = MENU_ACTIONS.get(choice)
        if action:
            action()
        else:
            warn(f"'{choice}' is not a valid option. Please choose 0–14.")
        input("\n  Press Enter to continue...")


def _find_project_by_title(title: str):
    title_lower = title.lower()
    for user in User.all_users:
        for project in user.projects:
            if project.title.lower() == title_lower:
                return project
    return None

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tracker")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p = sub.add_parser("add-user")
    p.add_argument("--name", required=True)
    p.add_argument("--email", required=True)
    p.set_defaults(func=cmd_add_user)

    p = sub.add_parser("list-users")
    p.set_defaults(func=cmd_list_users)

    p = sub.add_parser("delete-user")
    p.add_argument("--name", required=True)
    p.set_defaults(func=cmd_delete_user)

    p = sub.add_parser("add-project")
    p.add_argument("--user", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--due-date", dest="due_date", default="")
    p.set_defaults(func=cmd_add_project)

    p = sub.add_parser("list-projects")
    p.add_argument("--user", default="")
    p.set_defaults(func=cmd_list_projects)

    p = sub.add_parser("show-project")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_show_project)

    p = sub.add_parser("delete-project")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_delete_project)

    p = sub.add_parser("search-projects")
    p.add_argument("--query", required=True)
    p.set_defaults(func=cmd_search_projects)

    p = sub.add_parser("add-task")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--assign", default="")
    p.set_defaults(func=cmd_add_task)

    p = sub.add_parser("list-tasks")
    p.add_argument("--project", required=True)
    p.set_defaults(func=cmd_list_tasks)

    p = sub.add_parser("complete-task")
    p.add_argument("--project", required=True)
    p.add_argument("--task-id", dest="task_id", required=True, type=int)
    p.set_defaults(func=cmd_complete_task)

    p = sub.add_parser("update-task")
    p.add_argument("--project", required=True)
    p.add_argument("--task-id", dest="task_id", required=True, type=int)
    p.add_argument("--status", default="")
    p.add_argument("--assign", default="")
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_update_task)

    p = sub.add_parser("summary")
    p.set_defaults(func=cmd_summary)

    return parser

def main():
    try:
        load_data()
    except RuntimeError as exc:
        error(str(exc))
        sys.exit(1)

    if len(sys.argv) == 1:
        run_interactive_menu()
        sys.exit(0)

    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    exit_code = args.func(args)
    sys.exit(exit_code or 0)


if __name__ == "__main__":
    main()