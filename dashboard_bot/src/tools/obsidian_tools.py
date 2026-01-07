"""
Obsidian Vault Integration Tools.

Provides zero-config tools for creating and updating Daily Notes
in an Obsidian vault. Handles WSL/Windows path conversion automatically.
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import settings


def write_daily_note(content: str, date: Optional[str] = None) -> str:
    """Write or update a Daily Note in Obsidian vault.
    
    Creates or appends to a markdown file in the configured Obsidian vault
    using the standard Daily Notes naming convention (YYYY-MM-DD.md).
    
    Args:
        content: Markdown content for the daily note
        date: Date string in YYYY-MM-DD format, defaults to today
        
    Returns:
        Confirmation message with the file path on success.
        Returns error message if vault path is invalid or write fails.
        
    Example:
        >>> write_daily_note("## Tasks\\n- [ ] Review PRs", "2026-01-07")
        '✅ Daily note updated: /path/to/vault/Daily Notes/2026-01-07.md'
    """
    # Validate configuration
    if not settings.OBSIDIAN_VAULT_PATH:
        return json.dumps({
            "error": "OBSIDIAN_VAULT_PATH not configured in environment"
        })
    
    # Parse and validate date
    if date:
        try:
            note_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "error": f"Invalid date format: '{date}'. Use YYYY-MM-DD."
            })
    else:
        note_date = datetime.now()
    
    filename = note_date.strftime("%Y-%m-%d") + ".md"
    
    try:
        # Get the vault path with proper handling
        vault_path = _resolve_vault_path(settings.OBSIDIAN_VAULT_PATH)
        
        if not vault_path.exists():
            return json.dumps({
                "error": f"Vault path does not exist: {vault_path}"
            })
        
        # Create Daily Notes subdirectory if it doesn't exist
        daily_notes_dir = vault_path / "Daily Notes"
        daily_notes_dir.mkdir(parents=True, exist_ok=True)
        
        note_path = daily_notes_dir / filename
        
        print(f"   📝 Writing daily note: {filename}")
        
        # Check if file exists to decide between create or append
        if note_path.exists():
            # Append to existing note with a separator
            existing_content = note_path.read_text(encoding="utf-8")
            
            # Add timestamp separator
            timestamp = datetime.now().strftime("%H:%M")
            separator = f"\n\n---\n\n## Update at {timestamp}\n\n"
            
            new_content = existing_content + separator + content
            note_path.write_text(new_content, encoding="utf-8")
            
            print(f"   ✅ Appended to existing note")
            return f"✅ Daily note updated: {note_path}"
        else:
            # Create new note with frontmatter
            frontmatter = f"""---
date: {note_date.strftime("%Y-%m-%d")}
created: {datetime.now().isoformat()}
tags: [daily-note]
---

# {note_date.strftime("%A, %B %d, %Y")}

"""
            full_content = frontmatter + content
            note_path.write_text(full_content, encoding="utf-8")
            
            print(f"   ✅ Created new daily note")
            return f"✅ Daily note created: {note_path}"
            
    except PermissionError as e:
        error_msg = f"Permission denied writing to vault: {e}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})
        
    except Exception as e:
        error_msg = f"Error writing daily note: {type(e).__name__}: {e}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})


def read_daily_note(date: Optional[str] = None) -> str:
    """Read the content of a Daily Note from Obsidian vault.
    
    Args:
        date: Date string in YYYY-MM-DD format, defaults to today
        
    Returns:
        The content of the daily note, or error message if not found.
    """
    if not settings.OBSIDIAN_VAULT_PATH:
        return json.dumps({"error": "OBSIDIAN_VAULT_PATH not configured"})
    
    if date:
        try:
            note_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({"error": f"Invalid date format: '{date}'"})
    else:
        note_date = datetime.now()
    
    filename = note_date.strftime("%Y-%m-%d") + ".md"
    
    try:
        vault_path = _resolve_vault_path(settings.OBSIDIAN_VAULT_PATH)
        note_path = vault_path / "Daily Notes" / filename
        
        if not note_path.exists():
            return json.dumps({
                "error": f"Daily note not found: {filename}",
                "searched_path": str(note_path)
            })
        
        content = note_path.read_text(encoding="utf-8")
        return content
        
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


def append_to_daily_note(section: str, content: str, date: Optional[str] = None) -> str:
    """Append content to a specific section of today's Daily Note.
    
    Finds a section header (e.g., '## Tasks') and appends content below it.
    If the section doesn't exist, it will be created at the end.
    
    Args:
        section: The section header to append to (e.g., 'Tasks', 'Notes')
        content: The content to append to the section
        date: Date string in YYYY-MM-DD format, defaults to today
        
    Returns:
        Confirmation message on success, error message on failure.
    """
    if not settings.OBSIDIAN_VAULT_PATH:
        return json.dumps({"error": "OBSIDIAN_VAULT_PATH not configured"})
    
    if date:
        try:
            note_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({"error": f"Invalid date format: '{date}'"})
    else:
        note_date = datetime.now()
    
    filename = note_date.strftime("%Y-%m-%d") + ".md"
    
    try:
        vault_path = _resolve_vault_path(settings.OBSIDIAN_VAULT_PATH)
        daily_notes_dir = vault_path / "Daily Notes"
        daily_notes_dir.mkdir(parents=True, exist_ok=True)
        
        note_path = daily_notes_dir / filename
        
        # Normalize section header
        section_header = section if section.startswith("#") else f"## {section}"
        
        if note_path.exists():
            existing = note_path.read_text(encoding="utf-8")
            
            # Find the section and append after it
            pattern = rf"(^{re.escape(section_header)}.*$)"
            match = re.search(pattern, existing, re.MULTILINE)
            
            if match:
                # Insert content after section header
                insert_pos = match.end()
                new_content = existing[:insert_pos] + "\n" + content + existing[insert_pos:]
            else:
                # Section doesn't exist, add at end
                new_content = existing + f"\n\n{section_header}\n\n{content}"
            
            note_path.write_text(new_content, encoding="utf-8")
            return f"✅ Appended to section '{section}' in {filename}"
        else:
            # Create new note with the section
            return write_daily_note(f"{section_header}\n\n{content}", date)
            
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


def _resolve_vault_path(path_str: str) -> Path:
    """
    Resolve the vault path, handling WSL/Windows conversion.
    
    Automatically detects if running in WSL and converts Windows paths
    to their WSL equivalents.
    
    Args:
        path_str: Path string from configuration
        
    Returns:
        Resolved Path object
    """
    path = Path(path_str)
    
    # Check if we're running in WSL
    if _is_wsl():
        # If it looks like a Windows path, convert it
        if re.match(r'^[A-Za-z]:', path_str):
            # Convert Windows path to WSL path
            # C:\Users\... -> /mnt/c/Users/...
            drive_letter = path_str[0].lower()
            rest_of_path = path_str[2:].replace("\\", "/")
            wsl_path = f"/mnt/{drive_letter}{rest_of_path}"
            path = Path(wsl_path)
            print(f"   🔄 Converted to WSL path: {wsl_path}")
    else:
        # On Windows, normalize backslashes
        path = Path(path_str.replace("/", "\\"))
    
    return path.resolve()


def _is_wsl() -> bool:
    """
    Detect if running inside Windows Subsystem for Linux.
    
    Returns:
        True if running in WSL, False otherwise
    """
    # Check for WSL-specific indicators
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info or "wsl" in version_info
        except Exception:
            pass
    
    # Alternative: check for WSL environment variables
    return "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP" in os.environ
