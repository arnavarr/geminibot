"""
Dashboard Bot Configuration Module.

Configuración simplificada para el script de extracción de datos.
Solo incluye configuraciones para Jira, Outlook (MSAL), y Obsidian.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Dashboard Bot settings managed by Pydantic.
    
    Incluye configuraciones para:
    - Jira Cloud API
    - Microsoft Outlook (via MSAL)
    - Obsidian Vault management
    """

    # =========================================================================
    # Agent Configuration
    # =========================================================================
    AGENT_NAME: str = "DashboardBot"
    DEBUG_MODE: bool = False

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

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings instance
settings = Settings()
