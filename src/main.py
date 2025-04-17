import os
import sys
import argparse
from rich.console import Console
from rich.markdown import Markdown

from utils.config import (
    set_api_key_in_config,
    get_api_key_from_config,
)
from utils.git_utils import (
    run_git_diff,
    get_untracked_files,
)
from utils.ai_utils import get_diff_explanation


def main():
    console = Console()

    parser = argparse.ArgumentParser(
        description="Gitsplain - Make your Git diffs make sense.",
        epilog="""
Examples:
# Explain all current changes (tracked & untracked) vs HEAD
%(prog)s

# Explain staged changes only (untracked files ignored unless also passed as args)
%(prog)s --staged

# Explain changes between two commits (untracked files ignored)
%(prog)s HEAD~1 HEAD

# Show diff AND explain all current changes vs HEAD
%(prog)s --with-diff

# Only show diff for changes vs HEAD (untracked files ignored)
%(prog)s --diff-only HEAD

# Specify a different model
%(prog)s -d /path/to/my/repo --model gpt-4o-mini

# Set the API Key
%(prog)s --set-api-key
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    git_group = parser.add_argument_group("Git Diff Options")
    git_group.add_argument(
        "-d",
        "--repo-dir",
        default=".",
        help="Path to the Git repository directory (default: current directory)",
    )
    git_group.add_argument(
        "diff_args",
        nargs="*",
        help="Arguments to pass directly to 'git diff' (e.g., commit hashes, branch names, file paths, flags like --staged). Default: Compares working dir vs HEAD.",
    )

    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--model",
        default="gpt-4-turbo",
        help="OpenAI model to use for explanation (default: gpt-4-turbo)",
    )
    mode_group = output_group.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--with-diff",
        action="store_true",
        help="Show the original diff *before* the AI explanation.",
    )
    mode_group.add_argument(
        "--diff-only",
        action="store_true",
        help="Show *only* the original diff, do not request AI explanation.",
    )

    setting_group = parser.add_argument_group("Settings")
    setting_group.add_argument(
        "--set-api-key",
        action="store_true",
        help="Set the OpenAI API key in ~/.config/gitsplain/config.",
    )

    args = parser.parse_args()

    if args.set_api_key:
        api_key_input = input("Enter your OpenAI API key: ").strip()
        if not api_key_input:
            print("No API key entered.", file=sys.stderr)
            sys.exit(1)
        if set_api_key_in_config(api_key_input):
            sys.exit(0)
        else:
            sys.exit(1)

    diff_args_to_use = args.diff_args or ["HEAD"]
    diff_output = run_git_diff(args.repo_dir, diff_args_to_use)

    untracked_files = get_untracked_files(args.repo_dir)

    os.system("cls" if os.name == "nt" else "clear")

    if diff_output is None and untracked_files is None:
        print("ERROR: Failed to get information from git.", file=sys.stderr)
        sys.exit(1)

    diff_content = diff_output.strip() if diff_output else ""
    has_diff_changes = bool(diff_content)
    has_untracked_files = bool(untracked_files)

    if not has_diff_changes and not has_untracked_files:
        print("No changes (tracked or untracked) found.")
        sys.exit(0)

    if (args.with_diff or args.diff_only) and has_diff_changes:
        separator = (
            "\n" + "=" * 60 + "\n" if args.with_diff and not args.diff_only else ""
        )
        print("--- Original Git Diff ---")
        print(diff_content)
        if separator:
            print(separator, end="")
    elif (args.with_diff or args.diff_only) and not has_diff_changes:
        print("--- Original Git Diff ---")
        print("(No changes detected in tracked files for the specified diff command)")
        if args.with_diff and not args.diff_only:
            print("\n" + "=" * 60 + "\n", end="")

    if not args.diff_only:
        explanation = get_diff_explanation(
            diff_content,
            args.model,
            untracked_files,
        )

        if explanation:
            print("--- Gitsplain ---")
            print("--- AI Explanation ---")
            markdown = Markdown(explanation)
            console.print(markdown, soft_wrap=True)
            sys.exit(0)
        else:
            print("\nFailed to get AI explanation.", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
