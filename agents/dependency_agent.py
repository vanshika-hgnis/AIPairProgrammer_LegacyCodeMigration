import argparse
from pathlib import Path
from tools.graph_builder import build_repo_graph, save_graph
from rich.console import Console

console = Console()


def main():
    p = argparse.ArgumentParser(description="Build code dependency graph")
    p.add_argument("--repo", default=".", help="repository path")
    p.add_argument("--out", default="reports", help="output directory")
    p.add_argument(
        "--symbols", action="store_true", help="include symbol-level nodes (Python)"
    )
    p.add_argument(
        "--open",
        action="store_true",
        help="open the HTML after building (if available)",
    )
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    console.print(f"[cyan]Scanning repository:[/cyan] {repo}")
    g = build_repo_graph(str(repo), symbol_level=args.symbols)
    outs = save_graph(g, out_dir=args.out)
    console.print(f"[green]Saved graph files:[/green] {outs}")

    if args.open and outs.get("html"):
        import webbrowser

        webbrowser.open(str(Path(outs["html"]).resolve()))


if __name__ == "__main__":
    main()
