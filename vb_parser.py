import glob, re, os


def extract_vb_methods(repo_path, console):
    methods = []
    for file in glob.glob(os.path.join(repo_path, "**/*.vb"), recursive=True):
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        matches = re.findall(
            r"(?:Public|Private|Protected|Friend)\s+Sub\s+[\s\S]*?End\s+Sub", content
        )
        for m in matches:
            methods.append({"file": file, "code": m})
    console.print(f"[green]✅ Found {len(methods)} VB.NET methods[/green]")
    return methods
