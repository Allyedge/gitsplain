import os
import sys
import subprocess


def is_git_repository(path: str) -> bool:
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def run_git_diff(path: str, args: list[str]) -> str | None:
    if not os.path.isdir(path):
        print(f"ERROR: Path '{path}' is not a directory.", file=sys.stderr)
        return None

    if not is_git_repository(path):
        print(f"ERROR: Path '{path}' is not a git repository.", file=sys.stderr)
        return None

    command = ['git', 'diff']
    command.extend(args)

    print(f"Running command: {' '.join(command)} in {os.path.abspath(path)}", file=sys.stderr)
    print("-" * 20, file=sys.stderr)

    try:
        process = subprocess.run(
            command,
            cwd=path,
            check=False,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace"
        )

        if process.returncode != 0:
            if process.stderr:
                 print(f"ERROR: Git command failed:\n{process.stderr.strip()}", file=sys.stderr)
            else:
                 print(f"ERROR: Git command exited with status {process.returncode}", file=sys.stderr)

            return process.stdout.strip() if process.stdout else None

        return process.stdout.strip()

    except FileNotFoundError:
        print("ERROR: Git is not installed or not found in PATH.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        return None


def get_untracked_files(path: str) -> list[str] | None:
    if not os.path.isdir(path):
        print(f"ERROR: Path '{path}' is not a directory.", file=sys.stderr)
        return None

    if not is_git_repository(path):
        print(f"ERROR: Path '{path}' is not a git repository.", file=sys.stderr)
        return None

    try:
        process = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=path,
            check=False,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace"
        )

        if process.returncode != 0:
            if process.stderr:
                print(f"ERROR: Git command failed:\n{process.stderr.strip()}", file=sys.stderr)
            else:
                print(f"ERROR: Git command exited with status {process.returncode}", file=sys.stderr)
            return None

        untracked_files = process.stdout.strip().split('\n')
        return [f for f in untracked_files if f]

    except FileNotFoundError:
        print("ERROR: Git is not installed or not found in PATH.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        return None
