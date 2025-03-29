import os
import sys
import openai
from utils.config import get_api_key_from_config


def get_diff_explanation(
    diff_text: str, model: str, untracked_files: list[str] | None = None
) -> str | None:

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = get_api_key_from_config()

    if not api_key:
        print("ERROR: OpenAI API key is not found.", file=sys.stderr)
        print(
            "Please set the OPENAI_API_KEY environment variable or store it in ~/.config/gitsplain/config.",
            file=sys.stderr,
        )
        return None

    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}", file=sys.stderr)
        return None

    prompt_parts = [
        "You are an expert Git assistant. Your task is to analyze the following Git changes and provide a clear, concise summary and explanation suitable for a developer reviewing these changes.",
        "\nPlease structure your response as follows:",
        "1.  **High-Level Summary:** Briefly describe the overall purpose or nature of the changes (e.g., bug fix, feature implementation, refactoring, documentation update). Include mention of new files if any.",
        "2.  **Detailed Changes:** For each significantly changed file (or group of related files), explain the key modifications. Focus on *what* changed and *why* (if the reason is apparent from the code changes). Use Markdown for readability (like bullet points or code formatting where appropriate).",
        "3.  **New Files:** If there are new (untracked) files, list them and briefly describe their likely purpose based on their names or paths.",
    ]

    if diff_text and diff_text.strip():
        prompt_parts.extend(
            [
                "\nHere is the Git diff output for modified/deleted files:",
                "```diff",
                diff_text,
                "```",
            ]
        )
    else:
        prompt_parts.append(
            "\nThere were no changes detected by `git diff` (no modifications to tracked files)."
        )

    if untracked_files:
        prompt_parts.append(
            "\nAdditionally, the following files are newly created and untracked:"
        )
        for f in untracked_files:
            prompt_parts.append(f"- `{f}`")
        prompt_parts.append(
            "\nPlease include these new files in your summary and explanation."
        )
    else:
        prompt_parts.append("\nThere were no new untracked files detected.")

    prompt = "\n".join(prompt_parts)

    print(
        f"Prompting OpenAI API with model '{model}' for explanation...", file=sys.stderr
    )
    print("-" * 20, file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Git assistant providing clear summaries and explanations of git diffs and new files.",  # Slightly updated system message
                },
                {"role": "user", "content": prompt},
            ],
        )

        explanation = response.choices[0].message.content
        print("Explanation received.", file=sys.stderr)
        return explanation.strip() if explanation else "AI returned an empty response."

    except openai.AuthenticationError:
        print("\nERROR: OpenAI API key is invalid or missing.", file=sys.stderr)
        print("Please check your OPENAI_API_KEY environment variable.", file=sys.stderr)
        return None
    except openai.RateLimitError:
        print("\nERROR: OpenAI API rate limit exceeded.", file=sys.stderr)
        print(
            "Please check your OpenAI plan and usage, or wait before trying again.",
            file=sys.stderr,
        )
        return None
    except openai.APIConnectionError as e:
        print(f"\nERROR: Failed to connect to OpenAI API: {e}", file=sys.stderr)
        return None
    except openai.APITimeoutError:
        print("\nERROR: OpenAI API request timed out.", file=sys.stderr)
        return None
    except openai.APIStatusError as e:
        print(
            f"\nERROR: OpenAI API returned an error status: {e.status_code} - {e.response}",
            file=sys.stderr,
        )
        return None
    except Exception as e:
        print(
            f"\nERROR: An unexpected error occurred during OpenAI API call: {e}",
            file=sys.stderr,
        )
        return None
