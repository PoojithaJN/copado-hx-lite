import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table


load_dotenv()

APP_NAME = "copado-hx-lite"
STATE_FILE = Path(".copado-hx.json")

console = Console()
app = typer.Typer(
    name=APP_NAME,
    help="Agent-ready headless Salesforce DevOps CLI for CopadoCon Hackathon.",
    no_args_is_help=True,
)
auth_app = typer.Typer(help="Manage local demo authentication.")
story_app = typer.Typer(help="Inspect and select user stories.")
ai_app = typer.Typer(help="Ask demo AI agents for DevOps guidance.")
test_app = typer.Typer(help="List, run, and inspect automated tests.")

app.add_typer(auth_app, name="auth")
app.add_typer(story_app, name="story")
app.add_typer(ai_app, name="ai")
app.add_typer(test_app, name="test")


DEMO_STORIES = [
    {
        "id": "US-1234",
        "title": "Lead scoring automation",
        "status": "Ready for Commit",
        "branch": "feature/us-1234-lead-scoring",
        "owner": "Sales Ops",
        "metadata": ["Lead.Score__c", "LeadScoringFlow", "LeadTriggerHandler"],
    },
    {
        "id": "US-1235",
        "title": "Partner onboarding validation",
        "status": "In Progress",
        "branch": "feature/us-1235-partner-validation",
        "owner": "Partner Team",
        "metadata": ["Partner_Onboarding__c", "PartnerValidationRule"],
    },
    {
        "id": "US-1236",
        "title": "Case escalation dashboard",
        "status": "Ready for Test",
        "branch": "feature/us-1236-case-escalation",
        "owner": "Service Cloud",
        "metadata": ["Case_Escalation.dashboard", "EscalationQueue"],
    },
]

DEMO_TEST_JOBS = [
    {"job": "JOB-101", "name": "Apex regression suite", "status": "Available", "duration": "8m"},
    {"job": "JOB-102", "name": "Flow smoke tests", "status": "Available", "duration": "3m"},
    {"job": "JOB-103", "name": "Metadata validation", "status": "Available", "duration": "5m"},
]

DEMO_EXECUTIONS = {
    "EXE-101": {
        "job": "JOB-101",
        "status": "Passed",
        "started": "2026-06-01T09:00:00Z",
        "duration": "7m 42s",
        "passed": 42,
        "failed": 0,
        "coverage": "91%",
    }
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        console.print("[red]Local state file is invalid JSON: .copado-hx.json[/red]")
        raise typer.Exit(code=1)


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def require_auth() -> dict[str, Any]:
    state = load_state()
    if not state.get("auth", {}).get("token"):
        console.print(Panel("Run [bold]python main.py auth login --token demo-token[/bold] first.", title="Not authenticated"))
        raise typer.Exit(code=1)
    return state


def find_story(story_id: str) -> Optional[dict[str, Any]]:
    return next((story for story in DEMO_STORIES if story["id"] == story_id), None)


def selected_story(state: dict[str, Any]) -> Optional[dict[str, Any]]:
    story_id = state.get("selected_story")
    return find_story(story_id) if story_id else None


def latest_execution(state: dict[str, Any]) -> Optional[tuple[str, dict[str, Any]]]:
    execution_id = state.get("last_test_execution")
    if execution_id:
        executions = {**DEMO_EXECUTIONS, **state.get("executions", {})}
        execution = executions.get(execution_id)
        if execution:
            return execution_id, execution

    executions = state.get("executions", {})
    if executions:
        execution_id = next(reversed(executions))
        return execution_id, executions[execution_id]
    return None


def release_notes_for(story: dict[str, Any], state: dict[str, Any]) -> str:
    promotion = state.get("last_promotion", {})
    execution_info = latest_execution(state)
    execution_id = execution_info[0] if execution_info else "EXE-101"
    return (
        f"Delivered {story['title']} ({story['id']}). "
        f"Included metadata: {', '.join(story['metadata'])}. "
        f"Validation: {promotion.get('status', 'Validated')} to {promotion.get('env', 'UAT')}. "
        f"Regression: JOB-101 passed in {execution_id}."
    )


def status_model(state: dict[str, Any]) -> dict[str, Any]:
    story = selected_story(state)
    commit = state.get("last_commit")
    promotion = state.get("last_promotion")
    execution_info = latest_execution(state)
    return {
        "auth": "Authenticated" if state.get("auth", {}).get("token") else "Not authenticated",
        "selected_story": story,
        "last_commit": commit,
        "last_promotion": promotion,
        "last_test_execution": {"id": execution_info[0], **execution_info[1]} if execution_info else None,
        "release_notes": state.get("release_notes"),
    }


def dashboard_model(state: dict[str, Any]) -> dict[str, Any]:
    story = selected_story(state)
    commit = state.get("last_commit")
    promotion = state.get("last_promotion")
    execution_info = latest_execution(state)
    release_notes = state.get("release_notes")

    steps_done = [
        bool(story),
        bool(commit),
        bool(promotion),
        bool(execution_info and execution_info[1].get("status") == "Passed"),
        bool(release_notes),
    ]
    progress = round((sum(steps_done) / len(steps_done)) * 100)

    return {
        "selected_story": f"{story['id']} - {story['title']}" if story else "None",
        "commit_status": f"Created ({commit['id']})" if commit else "Not started",
        "validation_status": (
            f"{promotion['status']} to {promotion['env']}" if promotion else "Not started"
        ),
        "test_status": (
            f"{execution_info[1]['status']} ({execution_info[0]})" if execution_info else "Not started"
        ),
        "release_notes_status": "Generated" if release_notes else "Not generated",
        "overall_progress_percentage": progress,
    }


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2))


def show_ai_build_analysis(story: dict[str, Any]) -> None:
    table = Table(title="AI Build Analysis")
    table.add_column("Signal", style="cyan")
    table.add_column("Assessment")
    table.add_row("Story", f"{story['id']} - {story['title']}")
    table.add_row("Scope", ", ".join(story["metadata"]))
    table.add_row("Risk", "Low - story-scoped metadata only")
    table.add_row("Build Strategy", "Commit metadata, validate UAT, then run Apex regression")
    console.print(table)


def print_dashboard(data: dict[str, Any]) -> None:
    table = Table(title="Copado HX Lite Dashboard")
    table.add_column("Area", style="cyan")
    table.add_column("Status")
    table.add_row("Selected Story", data["selected_story"])
    table.add_row("Commit", data["commit_status"])
    table.add_row("Validation", data["validation_status"])
    table.add_row("Test", data["test_status"])
    table.add_row("Release Notes", data["release_notes_status"])
    table.add_row("Overall Progress", f"{data['overall_progress_percentage']}%")
    console.print(table)


@auth_app.command("login")
def auth_login(token: str = typer.Option(..., "--token", help="Demo token. Do not use real API keys.")) -> None:
    """Store demo auth locally."""
    state = load_state()
    state["auth"] = {
        "token": token,
        "mode": "demo",
        "login_time": now_iso(),
    }
    save_state(state)
    console.print(Panel("Authenticated in demo mode.", title="Copado HX Lite", style="green"))


@auth_app.command("status")
def auth_status() -> None:
    """Show local auth status."""
    state = load_state()
    auth = state.get("auth", {})
    if auth.get("token"):
        console.print(
            Panel(
                f"[green]Authenticated[/green]\nMode: {auth.get('mode', 'demo')}\nLogin: {auth.get('login_time', 'unknown')}",
                title="Auth Status",
            )
        )
        return
    console.print(Panel("[yellow]Not authenticated[/yellow]", title="Auth Status"))


@auth_app.command("logout")
def auth_logout() -> None:
    """Clear local demo auth."""
    state = load_state()
    state.pop("auth", None)
    save_state(state)
    console.print(Panel("Local demo auth cleared.", title="Logged out", style="yellow"))


@story_app.command("list")
def story_list() -> None:
    """List demo user stories."""
    require_auth()
    table = Table(title="Copado User Stories")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Status", style="magenta")
    table.add_column("Branch")
    table.add_column("Owner")
    for story in DEMO_STORIES:
        table.add_row(story["id"], story["title"], story["status"], story["branch"], story["owner"])
    console.print(table)


@story_app.command("set")
def story_set(story_id: str = typer.Option(..., "--id", help="User story ID, for example US-1234.")) -> None:
    """Select the active user story."""
    require_auth()
    story = find_story(story_id)
    if not story:
        console.print(f"[red]Unknown story:[/red] {story_id}")
        raise typer.Exit(code=1)
    state = load_state()
    state["selected_story"] = story_id
    save_state(state)
    console.print(Panel(f"{story_id}: {story['title']}", title="Selected Story", style="green"))


@story_app.command("show")
def story_show() -> None:
    """Show the selected user story."""
    state = require_auth()
    story = selected_story(state)
    if not story:
        console.print(Panel("No story selected. Run [bold]python main.py story set --id US-1234[/bold].", title="Story"))
        raise typer.Exit(code=1)

    metadata = "\n".join(f"- {item}" for item in story["metadata"])
    console.print(
        Panel(
            f"[bold]{story['id']}[/bold] - {story['title']}\n"
            f"Status: {story['status']}\n"
            f"Branch: {story['branch']}\n"
            f"Owner: {story['owner']}\n\n"
            f"[bold]Metadata[/bold]\n{metadata}",
            title="Active Story",
        )
    )


@ai_app.command("ask")
def ai_ask(
    prompt: str = typer.Argument(..., help="Question or generation request."),
    agent: str = typer.Option(..., "--agent", help="Demo agent name, for example build or release."),
) -> None:
    """Ask a demo AI agent."""
    state = require_auth()
    story = selected_story(state) or DEMO_STORIES[0]

    if agent.lower() == "build":
        answer = (
            f"For {story['id']}, commit the story-scoped metadata first: "
            f"{', '.join(story['metadata'])}. Run validation before promotion and keep unrelated org changes out."
        )
    elif agent.lower() == "release":
        answer = (
            f"Release notes draft:\n"
            f"- Delivered {story['title']} ({story['id']}).\n"
            f"- Included metadata: {', '.join(story['metadata'])}.\n"
            f"- Validation status: Apex regression passed in EXE-101."
        )
    else:
        answer = f"Demo {agent} agent received: {prompt}"

    console.print(Panel(answer, title=f"AI Agent: {agent}", style="blue"))


@app.command("commit")
def commit_changes(message: str = typer.Option(..., "--message", help="Commit message.")) -> None:
    """Create a demo Copado commit for the selected story."""
    state = require_auth()
    story = selected_story(state)
    if not story:
        console.print(Panel("Select a story before committing.", title="Commit blocked", style="yellow"))
        raise typer.Exit(code=1)

    commit_id = f"CMT-{datetime.now().strftime('%H%M%S')}"
    state["last_commit"] = {
        "id": commit_id,
        "story": story["id"],
        "message": message,
        "metadata": story["metadata"],
        "created_at": now_iso(),
    }
    save_state(state)

    table = Table(title="Demo Commit Created")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Commit", commit_id)
    table.add_row("Story", story["id"])
    table.add_row("Message", message)
    table.add_row("Metadata", ", ".join(story["metadata"]))
    console.print(table)


@app.command("promote")
def promote(
    env: str = typer.Option(..., "--env", help="Target environment, for example UAT or PROD."),
    validate: bool = typer.Option(False, "--validate", help="Run validation-only deployment."),
) -> None:
    """Promote the selected story to an environment."""
    state = require_auth()
    story = selected_story(state)
    if not story:
        console.print(Panel("Select a story before promotion.", title="Promotion blocked", style="yellow"))
        raise typer.Exit(code=1)

    target_env = env.upper()
    if target_env == "PROD":
        confirmed = Confirm.ask("Confirm PROD deployment?", default=False)
        if not confirmed:
            console.print("[yellow]PROD deployment cancelled.[/yellow]")
            raise typer.Exit(code=1)

    promotion = {
        "story": story["id"],
        "env": target_env,
        "mode": "Validation" if validate else "Deployment",
        "status": "Validated" if validate else "Promoted",
        "timestamp": now_iso(),
    }
    state["last_promotion"] = promotion
    save_state(state)

    console.print(
        Panel(
            f"Story: {story['id']}\nEnvironment: {target_env}\nMode: {promotion['mode']}\nStatus: {promotion['status']}",
            title="Promotion Complete",
            style="green",
        )
    )


@test_app.command("list")
def test_list() -> None:
    """List available demo test jobs."""
    require_auth()
    table = Table(title="Available Test Jobs")
    table.add_column("Job", style="cyan")
    table.add_column("Name")
    table.add_column("Status", style="green")
    table.add_column("Typical Duration")
    for job in DEMO_TEST_JOBS:
        table.add_row(job["job"], job["name"], job["status"], job["duration"])
    console.print(table)


@test_app.command("run")
def test_run(job: str = typer.Option(..., "--job", help="Job ID, for example JOB-101.")) -> None:
    """Start a demo test execution."""
    require_auth()
    test_job = next((item for item in DEMO_TEST_JOBS if item["job"] == job), None)
    if not test_job:
        console.print(f"[red]Unknown test job:[/red] {job}")
        raise typer.Exit(code=1)

    state = load_state()
    execution_id = "EXE-101" if job == "JOB-101" else f"EXE-{datetime.now().strftime('%H%M')}"
    execution = {
        "job": job,
        "status": "Passed",
        "started": now_iso(),
        "duration": test_job["duration"],
        "passed": 42 if job == "JOB-101" else 12,
        "failed": 0,
        "coverage": "91%" if job == "JOB-101" else "88%",
    }
    state.setdefault("executions", {})[execution_id] = execution
    state["last_test_execution"] = execution_id
    save_state(state)
    console.print(Panel(f"Started {test_job['name']}\nExecution: {execution_id}", title="Test Run", style="green"))


def get_execution(execution_id: str) -> dict[str, Any]:
    state = require_auth()
    executions = {**DEMO_EXECUTIONS, **state.get("executions", {})}
    execution = executions.get(execution_id)
    if not execution:
        console.print(f"[red]Unknown execution:[/red] {execution_id}")
        raise typer.Exit(code=1)
    return execution


@test_app.command("status")
def test_status(execution: str = typer.Option(..., "--execution", help="Execution ID, for example EXE-101.")) -> None:
    """Show test execution status."""
    result = get_execution(execution)
    console.print(
        Panel(
            f"Execution: {execution}\nJob: {result['job']}\nStatus: [green]{result['status']}[/green]\nDuration: {result['duration']}",
            title="Test Status",
        )
    )


@test_app.command("results")
def test_results(execution: str = typer.Option(..., "--execution", help="Execution ID, for example EXE-101.")) -> None:
    """Show test execution results."""
    result = get_execution(execution)
    table = Table(title=f"Test Results: {execution}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("Status", result["status"])
    table.add_row("Passed", str(result["passed"]))
    table.add_row("Failed", str(result["failed"]))
    table.add_row("Coverage", result["coverage"])
    table.add_row("Duration", result["duration"])
    console.print(table)


@app.command("status")
def status(json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON.")) -> None:
    """Show the current local Copado HX Lite workspace status."""
    state = load_state()
    data = status_model(state)

    if json_output:
        print_json(data)
        return

    table = Table(title="Copado HX Lite Status")
    table.add_column("Area", style="cyan")
    table.add_column("State")
    story = data["selected_story"]
    commit = data["last_commit"]
    promotion = data["last_promotion"]
    test_execution = data["last_test_execution"]
    release_notes = data["release_notes"]
    table.add_row("Auth", data["auth"])
    table.add_row("Selected Story", f"{story['id']} - {story['title']}" if story else "None")
    table.add_row("Last Commit", f"{commit['id']} - {commit['message']}" if commit else "None")
    table.add_row(
        "Last Promotion",
        f"{promotion['status']} to {promotion['env']} ({promotion['mode']})" if promotion else "None",
    )
    table.add_row(
        "Last Test",
        f"{test_execution['status']} ({test_execution['id']})" if test_execution else "None",
    )
    table.add_row("Release Notes", "Generated" if release_notes else "None")
    console.print(table)


@app.command("dashboard")
def dashboard(json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON.")) -> None:
    """Show a clean terminal dashboard for the current local workflow."""
    data = dashboard_model(load_state())
    if json_output:
        print_json(data)
        return
    print_dashboard(data)


@app.command("recommend")
def recommend() -> None:
    """Recommend the next best action based on local workflow state."""
    state = load_state()
    story = selected_story(state)
    commit = state.get("last_commit")
    promotion = state.get("last_promotion")
    execution_info = latest_execution(state)

    if not story:
        action = "Run python main.py story list, then python main.py story set --id US-1234."
        reason = "No user story is selected."
    elif not commit:
        action = f"Run python main.py commit --message \"feat: {story['title'].lower()}\"."
        reason = f"{story['id']} is selected, but no commit exists."
    elif not promotion:
        action = "Run python main.py promote --env UAT --validate."
        reason = f"Commit {commit['id']} is ready for validation."
    elif not execution_info:
        action = "Run python main.py test run --job JOB-101."
        reason = f"{promotion['status']} to {promotion['env']} is complete, but no test run is recorded."
    elif execution_info[1].get("status") == "Passed":
        action = "Run python main.py ai ask --agent release \"Generate release notes\" or python main.py dashboard."
        reason = f"Test execution {execution_info[0]} passed."
    else:
        action = "Run python main.py diagnose."
        reason = f"Test execution {execution_info[0]} needs attention."

    console.print(Panel(f"[bold]Recommended next action[/bold]\n{action}\n\n[bold]Reason[/bold]\n{reason}", title="Smart Recommendation", style="blue"))


@app.command("diagnose")
def diagnose() -> None:
    """Show an AI-style deployment failure diagnosis."""
    table = Table(title="AI Deployment Failure Diagnosis")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Failed Job ID", "DEPLOY-404")
    table.add_row("Root Cause", "Validation rule Lead_Score_Required__c expects Lead.Score__c on converted leads.")
    table.add_row("Suggested Fix", "Add a null-safe default in LeadScoringFlow before validation runs.")
    table.add_row("Confidence Score", "87%")
    table.add_row("Recommended Next Action", "Patch the flow mapping, recommit US-1234, then rerun UAT validation.")
    console.print(table)


@app.command("deliver")
def deliver(story_id: str = typer.Option(..., "--id", help="User story ID, for example US-1234.")) -> None:
    """Run an end-to-end simulated release workflow for a story."""
    require_auth()
    story = find_story(story_id)
    if not story:
        console.print(f"[red]Unknown story:[/red] {story_id}")
        raise typer.Exit(code=1)

    state = load_state()
    state["selected_story"] = story_id
    save_state(state)
    console.print(Panel(f"{story_id}: {story['title']}", title="Selected Story", style="green"))

    show_ai_build_analysis(story)

    steps = [
        "Creating Copado commit",
        "Validating promotion to UAT",
        "Running CRT test JOB-101",
        "Generating release notes",
    ]
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Simulated delivery workflow", total=len(steps))
        for step in steps:
            progress.update(task, description=step)
            time.sleep(0.15)
            progress.advance(task)

    commit_id = f"CMT-{datetime.now().strftime('%H%M%S')}"
    execution_id = "EXE-101"
    state = load_state()
    state["last_commit"] = {
        "id": commit_id,
        "story": story["id"],
        "message": f"feat: deliver {story['id']} {story['title'].lower()}",
        "metadata": story["metadata"],
        "created_at": now_iso(),
    }
    state["last_promotion"] = {
        "story": story["id"],
        "env": "UAT",
        "mode": "Validation",
        "status": "Validated",
        "timestamp": now_iso(),
    }
    state.setdefault("executions", {})[execution_id] = {
        "job": "JOB-101",
        "status": "Passed",
        "started": now_iso(),
        "duration": "7m 42s",
        "passed": 42,
        "failed": 0,
        "coverage": "91%",
    }
    state["last_test_execution"] = execution_id
    state["release_notes"] = {
        "story": story["id"],
        "generated_at": now_iso(),
        "body": release_notes_for(story, state),
    }
    save_state(state)

    commit_table = Table(title="Commit Created")
    commit_table.add_column("Field", style="cyan")
    commit_table.add_column("Value")
    commit_table.add_row("Commit", commit_id)
    commit_table.add_row("Story", story["id"])
    commit_table.add_row("Metadata", ", ".join(story["metadata"]))
    console.print(commit_table)

    console.print(Panel(f"Story: {story['id']}\nEnvironment: UAT\nMode: Validation\nStatus: Validated", title="Promotion Validation", style="green"))

    result = state["executions"][execution_id]
    result_table = Table(title=f"CRT Test Result: {execution_id}")
    result_table.add_column("Metric", style="cyan")
    result_table.add_column("Value")
    result_table.add_row("Job", result["job"])
    result_table.add_row("Status", result["status"])
    result_table.add_row("Passed", str(result["passed"]))
    result_table.add_row("Failed", str(result["failed"]))
    result_table.add_row("Coverage", result["coverage"])
    result_table.add_row("Duration", result["duration"])
    console.print(result_table)

    console.print(Panel(state["release_notes"]["body"], title="Release Notes", style="blue"))
    print_dashboard(dashboard_model(state))
    console.print(Panel("Browser tabs opened: 0", title="Final Delivery Summary", style="green"))


if __name__ == "__main__":
    app()
