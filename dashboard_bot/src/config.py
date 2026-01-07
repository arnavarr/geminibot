"""
Dashboard Bot Configuration Module.

Extends the Antigravity template Settings class with Dashboard-specific
configuration for Jira, Outlook (MSAL), and Obsidian integrations.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerConfig(BaseSettings):
    """Configuration for a single MCP server."""

    name: str = Field(description="Unique name for the MCP server")
    transport: str = Field(
        default="stdio", description="Transport type: stdio, http, sse"
    )
    command: Optional[str] = Field(
        default=None, description="Command to run for stdio transport"
    )
    args: List[str] = Field(
        default_factory=list, description="Arguments for the command"
    )
    url: Optional[str] = Field(default=None, description="URL for http/sse transport")
    env: dict = Field(
        default_factory=dict, description="Environment variables for the server"
    )
    enabled: bool = Field(default=True, description="Whether this server is enabled")

    model_config = SettingsConfigDict(extra="ignore")


class Settings(BaseSettings):
    """
    Dashboard Bot settings managed by Pydantic.
    
    Extends the base Antigravity template settings with integrations for:
    - Jira Cloud API
    - Microsoft Outlook (via MSAL)
    - Obsidian Vault management
    """

    # =========================================================================
    # Google GenAI Configuration
    # =========================================================================
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash-exp"

    # =========================================================================
    # Agent Configuration
    # =========================================================================
    AGENT_NAME: str = "DashboardBot"
    DEBUG_MODE: bool = False

    # =========================================================================
    # External LLM (OpenAI-compatible) Configuration
    # =========================================================================
    OPENAI_BASE_URL: str = Field(
        default="",
        description="Base URL for OpenAI-compatible API (e.g., http://localhost:11434/v1)",
    )
    OPENAI_API_KEY: str = Field(
        default="",
        description="API key for OpenAI-compatible endpoint. Leave blank if not required.",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="Default model name for OpenAI-compatible chat completions.",
    )

    # =========================================================================
    # Jira Cloud Configuration
    # =========================================================================
    JIRA_URL: str = Field(
        default="",
        description="Jira Cloud base URL (e.g., https://your-company.atlassian.net)",
    )
    JIRA_EMAIL: str = Field(
        default="",
        description="Email address for Jira API authentication",
    )
    JIRA_TOKEN: str = Field(
        default="",
        description="Jira API token for authentication",
    )

    # =========================================================================
    # Microsoft / Outlook Configuration (MSAL)
    # =========================================================================
    MS_CLIENT_ID: str = Field(
        default="",
        description="Azure AD Application (client) ID",
    )
    MS_AUTHORITY: str = Field(
        default="",
        description="Azure AD authority URL (e.g., https://login.microsoftonline.com/tenant_id)",
    )
    MS_SCOPES: str = Field(
        default="Mail.Read",
        description="Comma-separated list of Microsoft Graph scopes",
    )

    # =========================================================================
    # Obsidian Configuration
    # =========================================================================
    OBSIDIAN_VAULT_PATH: str = Field(
        default="",
        description="Absolute path to Obsidian vault directory",
    )

    # =========================================================================
    # Memory Configuration
    # =========================================================================
    MEMORY_FILE: str = "agent_memory.json"

    # =========================================================================
    # MCP Configuration
    # =========================================================================
    MCP_ENABLED: bool = Field(default=False, description="Enable MCP integration")
    MCP_SERVERS_CONFIG: str = Field(
        default="mcp_servers.json", description="Path to MCP servers configuration file"
    )
    MCP_CONNECTION_TIMEOUT: int = Field(
        default=30, description="Timeout in seconds for MCP server connections"
    )
    MCP_TOOL_PREFIX: str = Field(
        default="mcp_", description="Prefix for MCP tool names to avoid conflicts"
    )

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings instance
settings = Settings()
