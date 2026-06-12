from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def success(msg: str):
    console.print(f"OK {msg}")

def error(msg: str):
    console.print(f"ERROR {msg}")

def warn(msg: str):
    console.print(f"WARN {msg}")

def info(msg: str):
    console.print(f"INFO {msg}")

def print_users(users):
    if not users:
        warn("No users found.")
        return

    table = Table(
        title="[bold]All Users[/bold]",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold magenta",
    )
    table.add_column("ID", style="dim", width=5)
    table.add_column("Name", style="bold")
    table.add_column("Email")
    table.add_column("Projects", justify="center")

    for u in users:
        table.add_row(str(u.id), u.name, u.email, str(len(u.projects)))

    console.print(table)

def print_projects(projects, heading: str = "Projects"):
    if not projects:
        warn("No projects found.")
        return

    table = Table(
        title=f"[bold]{heading}[/bold]",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold blue",
    )
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Owner")
    table.add_column("Due Date")
    table.add_column("Tasks", justify="center")
    table.add_column("Description")

    for p in projects:
        due = p.due_date or "[dim]—[/dim]"
        desc = p.description[:50] + "…" if len(p.description) > 50 else p.description
        table.add_row(
            str(p.id), p.title, p.owner, due, str(len(p.tasks)), desc or "[dim]—[/dim]"
        )

    console.print(table)

STATUS_STYLE = {
    "pending": "[yellow]pending[/yellow]",
    "in_progress": "[blue]in progress[/blue]",
    "complete": "[green]complete[/green]",
}

def print_tasks(tasks, project_title: str = ""):
    if not tasks:
        warn("No tasks found.")
        return

    heading = f"Tasks — {project_title}" if project_title else "Tasks"
    table = Table(
        title=f"[bold]{heading}[/bold]",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Assigned To")
    table.add_column("Status")
    table.add_column("Created")

    for t in tasks:
        status_display = STATUS_STYLE.get(t.status, t.status)
        created = t.created_at[:10] if t.created_at else "—"
        table.add_row(
            str(t.id), t.title, t.assigned_to, status_display, created
        )

    console.print(table)


def print_project_detail(project):
    lines = [
        f"[bold]Title:[/bold]       {project.title}",
        f"[bold]Owner:[/bold]       {project.owner}",
        f"[bold]Due Date:[/bold]    {project.due_date or '—'}",
        f"[bold]Description:[/bold] {project.description or '—'}",
        f"[bold]Created:[/bold]     {project.created_at[:10]}",
        f"[bold]Tasks:[/bold]       {len(project.tasks)} total "
        f"({len(project.complete_tasks())} complete, "
        f"{len(project.pending_tasks())} pending)",
    ]
    console.print(Panel("\n".join(lines), title=f"Project #{project.id}", expand=False))
    if project.tasks:
        print_tasks(project.tasks, project.title)
