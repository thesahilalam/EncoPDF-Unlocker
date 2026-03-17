import os, sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()

def ensure_folders():
    for folder in ["wordlists", "logs", "sessions"]:
        if not os.path.exists(folder): os.makedirs(folder)

def display_banner(total, optimal):
    os.system('clear' if os.name == 'posix' else 'cls')
    banner_text = (
        "[bold cyan]      📂 ENCOPDF-UNLOCKER v1.0[/bold cyan]\n"
        "[dim]   Advanced PDF Recovery & Security Suite[/dim]\n"
        "──────────────────────────────────────────\n"
        f"[bold white]System:[/bold white] {total} Cores | [bold green]Using {optimal} Cores (80%)[/bold green]\n"
        "[bold yellow]Developer:[/bold yellow] [link=https://github.com/thesahilalam]@thesahilalam[/link]"
    )
    console.print(Panel(banner_text, border_style="bold blue", expand=False, padding=(1, 2)))

def clean_path(path):
    return path.strip().replace("'", "").replace('"', "").replace("\\ ", " ")

def save_to_log(filename, password, time_taken):
    ensure_folders()
    with open("logs/success.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] File: {filename} | Password: {password} | Time: {time_taken}\n")