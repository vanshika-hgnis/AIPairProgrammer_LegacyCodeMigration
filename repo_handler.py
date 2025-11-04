import os, tempfile
from git import Repo
from rich.panel import Panel


def clone_or_load_repo(repo_url, console):
    if os.path.isdir(repo_url):
        console.print(f"[yellow]📁 Using local path:[/yellow] {repo_url}")
        return repo_url
    tmp_dir = tempfile.mkdtemp()
    console.print(Panel.fit(f"Cloning repo from [blue]{repo_url}[/blue] ..."))
    Repo.clone_from(repo_url, tmp_dir)
    return tmp_dir
