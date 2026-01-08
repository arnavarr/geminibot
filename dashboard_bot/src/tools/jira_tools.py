"""
Jira Cloud Integration Tools.

Provides zero-config tools for querying Jira Cloud using JQL.
Credentials are loaded from environment variables via the config module.
"""

import json
from typing import List, Dict, Any
from urllib.parse import quote

import requests

from src.config import settings


def search_jira_issues(jql: str) -> str:
    """Search Jira issues using JQL query.
    
    Queries the Jira Cloud REST API v3 with the provided JQL string
    and returns a JSON-formatted list of matching issues.
    
    Args:
        jql: JQL query string (e.g., 'project = OD AND status != Done ORDER BY updated DESC')
        
    Returns:
        JSON string containing list of issues with key, summary, status, priority, and updated fields.
        Returns error message if the request fails.
        
    Example:
        >>> search_jira_issues('project = OD AND assignee = currentUser()')
        '[{"key": "OD-123", "summary": "Fix login bug", "status": "In Progress", ...}]'
    """
    # Validate configuration
    if not settings.JIRA_URL:
        return json.dumps({"error": "JIRA_URL not configured in environment"})
    if not settings.JIRA_EMAIL or not settings.JIRA_TOKEN:
        return json.dumps({"error": "JIRA_EMAIL and JIRA_TOKEN must be configured"})
    
    # Build API URL for new JQL endpoint
    base_url = settings.JIRA_URL.rstrip("/")
    api_url = f"{base_url}/rest/api/3/search/jql"
    
    # Set up authentication (Basic Auth with API token)
    auth = (settings.JIRA_EMAIL, settings.JIRA_TOKEN)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Request body for POST method
    payload = {
        "jql": jql,
        "fields": ["key", "summary", "status", "priority", "updated", "assignee"],
        "maxResults": 50
    }
    
    try:
        print(f"   🔍 Querying Jira: {jql[:50]}{'...' if len(jql) > 50 else ''}")
        
        response = requests.post(
            api_url,
            auth=auth,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("issues", [])
        
        # Extract relevant fields from each issue
        result: List[Dict[str, Any]] = []
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Safely extract nested fields
            status_obj = fields.get("status", {})
            priority_obj = fields.get("priority", {})
            assignee_obj = fields.get("assignee", {})
            
            result.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": status_obj.get("name") if status_obj else None,
                "priority": priority_obj.get("name") if priority_obj else None,
                "updated": fields.get("updated"),
                "assignee": assignee_obj.get("displayName") if assignee_obj else None
            })
        
        print(f"   ✅ Found {len(result)} issues")
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"Jira API error: {e.response.status_code}"
        try:
            error_detail = e.response.json()
            error_msg += f" - {error_detail.get('errorMessages', [e.response.text])}"
        except (ValueError, json.JSONDecodeError):
            error_msg += f" - {e.response.text}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})
        
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: Unable to reach Jira at {settings.JIRA_URL}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})
        
    except requests.exceptions.Timeout:
        error_msg = "Request timed out while connecting to Jira"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON response from Jira: {e}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})
        
    except Exception as e:
        error_msg = f"Unexpected error querying Jira: {type(e).__name__}: {e}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})


def get_jira_issue(issue_key: str) -> str:
    """Get details for a specific Jira issue.
    
    Retrieves detailed information about a single Jira issue by its key.
    
    Args:
        issue_key: The Jira issue key (e.g., 'OD-123', 'VUL-456')
        
    Returns:
        JSON string with issue details including description and comments.
        Returns error message if the request fails.
    """
    if not settings.JIRA_URL:
        return json.dumps({"error": "JIRA_URL not configured"})
    if not settings.JIRA_EMAIL or not settings.JIRA_TOKEN:
        return json.dumps({"error": "JIRA credentials not configured"})
    
    base_url = settings.JIRA_URL.rstrip("/")
    api_url = f"{base_url}/rest/api/3/issue/{issue_key}"
    
    auth = (settings.JIRA_EMAIL, settings.JIRA_TOKEN)
    headers = {"Accept": "application/json"}
    
    try:
        print(f"   🔍 Fetching Jira issue: {issue_key}")
        response = requests.get(api_url, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        fields = data.get("fields", {})
        
        result = {
            "key": data.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "description": _extract_text_from_adf(fields.get("description")),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            "created": fields.get("created"),
            "updated": fields.get("updated")
        }
        
        print(f"   ✅ Retrieved issue: {issue_key}")
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({"error": f"Issue '{issue_key}' not found"})
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"})
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


def get_all_my_issues() -> List[Dict[str, Any]]:
    """Obtiene TODAS las tareas asignadas al usuario actual.
    
    Ejecuta JQL: assignee = currentUser() ORDER BY updated DESC
    No requiere parámetros de entrada (determinista).
    
    Returns:
        Lista de diccionarios con información de cada tarea.
        Cada diccionario contiene: key, summary, status, priority, description, updated.
        Retorna lista vacía si hay error.
        
    Example:
        >>> tasks = get_all_my_issues()
        >>> [{'key': 'OD-123', 'summary': 'Fix login bug', 'status': 'In Progress', ...}]
    """
    # Validate configuration
    if not settings.JIRA_URL:
        print("   ❌ JIRA_URL not configured in environment")
        return []
    if not settings.JIRA_EMAIL or not settings.JIRA_TOKEN:
        print("   ❌ JIRA_EMAIL and JIRA_TOKEN must be configured")
        return []
    
    # Fixed JQL for current user's tasks
    jql = "assignee = currentUser() ORDER BY updated DESC"
    
    # Build API URL for new JQL endpoint
    base_url = settings.JIRA_URL.rstrip("/")
    api_url = f"{base_url}/rest/api/3/search/jql"
    
    # Set up authentication (Basic Auth with API token)
    auth = (settings.JIRA_EMAIL, settings.JIRA_TOKEN)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Request body for POST method
    payload = {
        "jql": jql,
        "fields": ["key", "summary", "status", "priority", "updated", "assignee", "description"],
        "maxResults": 100
    }
    
    try:
        print(f"   🔍 Obteniendo tareas de Jira (assignee = currentUser())...")
        
        response = requests.post(
            api_url,
            auth=auth,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("issues", [])
        
        # Extract relevant fields from each issue
        result: List[Dict[str, Any]] = []
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Safely extract nested fields
            status_obj = fields.get("status", {})
            priority_obj = fields.get("priority", {})
            
            result.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": status_obj.get("name") if status_obj else None,
                "priority": priority_obj.get("name") if priority_obj else None,
                "description": _extract_text_from_adf(fields.get("description")),
                "updated": fields.get("updated"),
            })
        
        print(f"   ✅ Encontradas {len(result)} tareas")
        return result
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"Jira API error: {e.response.status_code}"
        try:
            error_detail = e.response.json()
            error_msg += f" - {error_detail.get('errorMessages', [e.response.text])}"
        except (ValueError, json.JSONDecodeError):
            error_msg += f" - {e.response.text}"
        print(f"   ❌ {error_msg}")
        return []
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error: Unable to reach Jira at {settings.JIRA_URL}")
        return []
        
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out while connecting to Jira")
        return []
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response from Jira: {e}")
        return []
        
    except Exception as e:
        print(f"   ❌ Unexpected error querying Jira: {type(e).__name__}: {e}")
        return []


def _extract_text_from_adf(adf_content: Any) -> str:
    """
    Extract plain text from Atlassian Document Format (ADF) content.
    
    Args:
        adf_content: ADF structured content from Jira API
        
    Returns:
        Plain text extracted from the ADF structure
    """
    if not adf_content:
        return ""
    
    if isinstance(adf_content, str):
        return adf_content
    
    if not isinstance(adf_content, dict):
        return str(adf_content)
    
    text_parts = []
    
    def extract_recursive(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                text_parts.append(node.get("text", ""))
            for child in node.get("content", []):
                extract_recursive(child)
        elif isinstance(node, list):
            for item in node:
                extract_recursive(item)
    
    extract_recursive(adf_content)
    return " ".join(text_parts)
