"""
Convenience entrypoint so `python agent.py` works from the repo root.

Ejecuta el DataCollector para extraer datos de Jira y Outlook.
"""

from src.agent import DataCollector


def main():
    collector = DataCollector()
    collector.run()


if __name__ == "__main__":
    main()
