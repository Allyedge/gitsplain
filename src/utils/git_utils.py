import os
import sys
import subprocess


def is_git_repository(path: str) -> bool:
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def run_git_diff(path: str, args: list[str]) -> str | None:
    if not os.path.isdir(path):
        print(f"ERROR: Path '{path}' is not a directory.")
        return None

    if not is_git_repository(path):
        print(f"ERROR: Path '{path}' is not a git repository.")
        return None

    command = ["git", "diff"]
    command.extend(args)

    print(
        f"Running command: {' '.join(command)} in {os.path.abspath(path)}",
        file=sys.stderr,
    )
    print("-" * 20, file=sys.stderr)

    try:
        process = subprocess.run(
            command,
            cwd=path,
            check=False,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )

        if process.returncode != 0:
            if process.stderr:
                print(
                    f"ERROR: Git command failed:\n{process.stderr.strip()}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"ERROR: Git command exited with status {process.returncode}",
                    file=sys.stderr,
                )

            return process.stdout.strip() if process.stdout else None

        return process.stdout.strip()

    except FileNotFoundError:
        print("ERROR: Git is not installed or not found in PATH.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        return None


def get_untracked_files(repo_path: str) -> list[str] | None:
    if not is_git_repository(repo_path):
        print(f"ERROR: Path '{repo_path}' is not a git repository.", file=sys.stderr)
        return None

    abs_repo_path = os.path.abspath(repo_path)

    command = ["git", "status", "--porcelain=v1", "--untracked-files=all"]
    print(f"Running command: {' '.join(command)} in {abs_repo_path}", file=sys.stderr)
    print("-" * 20, file=sys.stderr)

    try:
        process = subprocess.run(
            command,
            cwd=abs_repo_path,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if process.returncode != 0:
            print(
                f"ERROR: 'git status' failed:\n{process.stderr.strip()}",
                file=sys.stderr,
            )
            return None

        untracked = []
        for line in process.stdout.strip().splitlines():
            if line.startswith("?? "):
                filepath = line[3:].strip()
                if (
                    len(filepath) >= 2
                    and filepath.startswith('"')
                    and filepath.endswith('"')
                ):
                    try:
                        filepath = (
                            filepath[1:-1]
                            .encode("latin-1", "backslashreplace")
                            .decode("unicode-escape")
                        )
                    except Exception:
                        filepath = filepath[1:-1]
                untracked.append(filepath)
        return untracked

    except FileNotFoundError:
        print("ERROR: Git is not installed or not found in PATH.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to get untracked files: {e}", file=sys.stderr)
        return None
