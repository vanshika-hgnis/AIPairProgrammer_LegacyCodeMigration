import stat, time, shutil
import os

def handle_remove_readonly(func, path, exc_info):
    """Force delete read-only or locked files (Windows safe)."""
    import errno
    excvalue = exc_info[1]
    if func in (os.unlink, os.rmdir) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

def clone_or_load_repo(repo_url, console):
    repo_dir = os.path.join("repos", "current_repo")

    if os.path.exists(repo_dir):
        console.print("[yellow]⚠ Removing previous repo safely...[/yellow]")
        for _ in range(3):  # Retry loop for Windows file locks
            try:
                shutil.rmtree(repo_dir, onerror=handle_remove_readonly)
                break
            except PermissionError:
                console.print("[red]Repo still in use — retrying in 2s...[/red]")
                time.sleep(2)
        else:
            raise RuntimeError("❌ Could not remove repo folder — try closing any Git tools")

    # now clone fresh
    os.system(f"git clone {repo_url} {repo_dir}")
    console.print(f"[green]✅ Repo cloned to {repo_dir}[/green]")
    return os.path.abspath(repo_dir)