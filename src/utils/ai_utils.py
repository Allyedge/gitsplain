import sys
import openai
from utils.config import get_api_key_from_config


def get_diff_explanation(
    diff_text: str, model: str, untracked_files: list[str] | None = None
) -> str | None:
    api_key = get_api_key_from_config()

    if not api_key:
        print("ERROR: OpenAI API key is not found.", file=sys.stderr)
        print(
            "Please set the OPENAI_API_KEY environment variable or use --set-api-key.",
            file=sys.stderr,
        )
        return None

    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}", file=sys.stderr)
        return None

    prompt_lines = [
        "## ROLE: Expert Git Analyst & Code Review Assistant",
        "## GOAL: Generate a comprehensive, developer-focused analysis of the provided Git changes, evaluating both technical implementation and PR readiness. Your analysis should be clear, concise, and technically accurate, suitable for a code review context.",
        "\n## INPUTS:",
        "1.  **Git Diff Output:** Changes to tracked files (modifications, deletions). Provided below under `### Git Diff Output`. May be empty if only untracked files changed.",
        "2.  **Untracked Files List:** New files not yet tracked by Git. Provided below under `### Untracked Files List`. May be empty.",
        "\n## REQUIRED OUTPUT STRUCTURE (Use Markdown):",
        "### 1. Overall Summary",
        "-   Provide a high-level paragraph summarizing the primary purpose and nature of ALL changes (e.g., bug fix, feature implementation, refactoring, documentation, adding new module).",
        "-   Mention the key files or areas affected, including both modified and new files.",
        "-   **PR Readiness Assessment:** Briefly state whether the changes appear ready for PR review (e.g., 'Changes appear PR-ready with minor suggestions', 'Needs additional work before PR submission').",
        "\n### 2. Modified/Deleted Files (from Diff)",
        '-   If the Git Diff Output is empty, state: "No changes detected in tracked files."',
        "-   Otherwise, for EACH file listed in the diff:",
        "    -   **`[Filename]`** (e.g., `src/utils/git_utils.py`)",
        "        -   **What Changed:** Bullet points detailing the specific code/content modifications (e.g., 'Added function `X` to handle Y', 'Removed unused variable `Z`', 'Modified logic in `func_A` for edge case B', 'Updated documentation section C'). Be specific.",
        "        -   **Why (Inferred):** Briefly explain the *likely* reason for the change based on the code context (e.g., 'To fix bug #123', 'To implement feature request Y', 'To improve performance by Z', 'To adhere to new style guide'). If the reason isn't clear, state 'Reason not immediately apparent from diff'.",
        "        -   **Code Quality Assessment:**",
        "            -   **Strengths:** Note positive aspects (e.g., 'Clean implementation', 'Good error handling', 'Clear documentation', 'Efficient algorithm choice').",
        "            -   **Areas for Improvement:** Suggest potential improvements (e.g., 'Could add input validation', 'Consider adding error logging', 'Might benefit from unit tests', 'Documentation could be more detailed').",
        "        -   **Potential Impact/Review Focus:** Note any potential side effects, areas needing careful review, or dependencies introduced/removed (e.g., 'Might affect downstream callers of `func_A`', 'Ensure tests cover the new edge case', 'Check configuration file for corresponding changes').",
        "\n### 3. New Untracked Files",
        '-   If the Untracked Files List is empty, state: "No new untracked files detected."',
        "-   Otherwise, for EACH file listed:",
        "    -   **`[Filename]`** (e.g., `tests/test_new_feature.py`)",
        "        -   **Purpose (Inferred):** Describe the likely purpose based on the filename, path, and common conventions (e.g., 'New unit tests for feature X', 'Configuration file for service Y', 'Utility script for task Z', 'Data fixture for testing').",
        "        -   **Key Contents (If Obvious):** Briefly mention expected contents if the file type suggests it (e.g., 'Likely contains test cases using `pytest`', 'Probably defines constants or settings', 'Appears to be a shell script').",
        "        -   **Quality Assessment:** Evaluate the apparent quality and completeness of the new file (e.g., 'Appears to follow project conventions', 'Might need additional documentation', 'Consider adding error handling').",
        "\n### 4. PR Readiness & Quality Metrics",
        "-   **Overall Code Quality:**",
        "    -   Rate the overall code quality (High/Medium/Low) and explain why.",
        "    -   Note any consistent patterns (good or bad) across the changes.",
        "-   **Testing Coverage:**",
        "    -   Assess whether the changes appear to be adequately tested.",
        "    -   Suggest any missing test cases or areas that need testing.",
        "-   **Documentation:**",
        "    -   Evaluate the completeness and clarity of documentation.",
        "    -   Suggest any missing or unclear documentation.",
        "-   **Style & Conventions:**",
        "    -   Note adherence to project style and conventions.",
        "    -   Point out any style inconsistencies.",
        "-   **Security Considerations:**",
        "    -   Flag any potential security concerns.",
        "    -   Suggest security-related improvements if needed.",
        "\n### 5. Recommendations & Next Steps",
        "-   List specific actionable recommendations for improvement.",
        "-   Prioritize the recommendations (Critical/Important/Nice to have).",
        "-   Suggest any follow-up tasks or investigations needed.",
        "\n## STYLE GUIDELINES:",
        "-   Use clear and concise technical language.",
        "-   Format output using Markdown (headings, bullet points, bold text, `inline code`).",
        "-   Be objective and constructive in feedback.",
        "-   Focus on actionable insights rather than just observations.",
        "\n--- START OF PROVIDED DATA ---",
    ]

    if diff_text and diff_text.strip():
        prompt_lines.append("```diff")
        prompt_lines.append(diff_text.strip())
        prompt_lines.append("```")
    else:
        prompt_lines.append("(No changes detected by `git diff` in tracked files)")

    prompt_lines.append("\n### Untracked Files List:")
    if untracked_files:
        for f in untracked_files:
            prompt_lines.append(f"- `{f}`")
    else:
        prompt_lines.append("(No new untracked files detected)")

    prompt_lines.append("\n--- END OF PROVIDED DATA ---")
    prompt_lines.append("\n## GENERATE EXPLANATION:")

    prompt = "\n".join(prompt_lines)

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
                    "content": "You are an expert Git Analyst AI assistant. You analyze git diffs and untracked file lists to provide comprehensive, developer-focused explanations following a specific Markdown structure.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        explanation = response.choices[0].message.content
        print("Explanation received.", file=sys.stderr)
        return explanation.strip() if explanation else "AI returned an empty response."

    except openai.AuthenticationError:
        print("\\nERROR: OpenAI API key is invalid or missing.", file=sys.stderr)
        print(
            "Please check your OPENAI_API_KEY environment variable or use --set-api-key.",
            file=sys.stderr,
        )
        return None
    except openai.RateLimitError:
        print("\\nERROR: OpenAI API rate limit exceeded.", file=sys.stderr)
        print(
            "Please check your OpenAI plan and usage, or wait before trying again.",
            file=sys.stderr,
        )
        return None
    except openai.APIConnectionError as e:
        print(f"\\nERROR: Failed to connect to OpenAI API: {e}", file=sys.stderr)
        return None
    except openai.APITimeoutError:
        print("\\nERROR: OpenAI API request timed out.", file=sys.stderr)
        return None
    except openai.APIStatusError as e:
        print(
            f"\\nERROR: OpenAI API returned an error status: {e.status_code} - {e.response}",
            file=sys.stderr,
        )
        return None
    except Exception as e:
        print(
            f"\\nERROR: An unexpected error occurred during OpenAI API call: {e}",
            file=sys.stderr,
        )
        return None
