# Dashboard Bot

**Objective:** Act as a Personal Executive Assistant for development team leads.

## Description

The Dashboard Bot is an intelligent agent designed to streamline your morning routine. It connects to your essential tools to:

1. **Query Jira** for critical alerts and pending tasks.
2. **Review unread Outlook emails** to identify communications requiring attention.
3. **Synthesize all information** into a perfectly formatted Daily Note in Obsidian.

## Features

- **Jira Integration**: Fetch high-priority issues and custom JQL queries.
- **Outlook Integration**: Retrieve unread emails from the last 24 hours.
- **Obsidian Support**: Automatically generate and append to Daily Notes following a specific template.
- **Secure Configuration**: Uses `.env` for credential management.

## Prerequisites

- Python 3.8 or higher
- Git

## Installation

### Automatic Installation (Linux/macOS)

The included installer sets up the virtual environment, installs dependencies, and initializes configuration.

```bash
./install.sh
```

### Manual Installation (Windows/Linux/macOS)

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd dashboard_bot
    ```

2. **Create and activate a virtual environment:**

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    Copy the example configuration file:

    ```bash
    # Windows
    copy .env.example .env

    # Linux/macOS
    cp .env.example .env
    ```

    Open `.env` and fill in your API keys and paths:
    - `GOOGLE_API_KEY`: For Gemini AI.
    - `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`: For Jira access.
    - `MS_CLIENT_ID`, `MS_AUTHORITY`: For Outlook access.
    - `OBSIDIAN_VAULT_PATH`: Absolute path to your Obsidian vault.

## Usage

Ensure your virtual environment is activated, then run the agent with a natural language task:

```bash
python agent.py "Create today's daily note with my Jira tasks and emails"
```

Or simply:

```bash
python agent.py
```

(Defaults to the standard daily briefing task)

## Project Structure

- `src/`: Core agent logic and tools.
- `tests/`: Unit and integration tests.
- `openspec/`: OpenSpec definitions.
- `artifacts/`: Generated outputs.
- `agent.py`: Entry point script.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
