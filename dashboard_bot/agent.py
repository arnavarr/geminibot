"""
Convenience entrypoint so `python agent.py` works from the repo root.

You can pass the task via CLI args or the AGENT_TASK env var.
Example:
    python agent.py "Create today's daily note with my Jira tasks and emails"
"""
import os
import sys

from src.agent import GeminiAgent


def main():
    task = " ".join(sys.argv[1:]).strip() or os.environ.get(
        "AGENT_TASK", "Create today's daily note with my Jira tasks and emails"
    )

    agent = GeminiAgent()
    try:
        agent.run(task)
    finally:
        agent.shutdown()


if __name__ == "__main__":
    main()
