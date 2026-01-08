"""
Outlook Email Integration Tools.

Provides zero-config tools for fetching emails using Microsoft Graph API
with MSAL (Microsoft Authentication Library) for OAuth2 authentication.
"""

import json
from typing import Optional, Dict, Any, List

from src.config import settings

# Try to import MSAL - graceful fallback if not installed
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False


def fetch_recent_emails(limit: int = 10) -> str:
    """Fetch recent unread emails from Outlook.
    
    Queries Microsoft Graph API for recent unread emails using MSAL
    for authentication. Returns a formatted list of sender and subject.
    
    Args:
        limit: Maximum number of emails to retrieve (default: 10, max: 50)
        
    Returns:
        Formatted string with sender and subject for each email.
        Returns error message if authentication fails or API is unavailable.
        
    Example:
        >>> fetch_recent_emails(5)
        '📧 Recent Emails (5):
         1. From: john@example.com | Subject: Meeting tomorrow
         2. From: alerts@jira.com | Subject: [OD-123] Task assigned'
    """
    if not MSAL_AVAILABLE:
        return json.dumps({
            "error": "MSAL library not installed. Run: pip install msal"
        })
    
    # Validate configuration
    if not settings.MS_CLIENT_ID:
        return json.dumps({"error": "MS_CLIENT_ID not configured in environment"})
    if not settings.MS_AUTHORITY:
        return json.dumps({"error": "MS_AUTHORITY not configured in environment"})
    
    # Clamp limit to reasonable range
    limit = max(1, min(limit, 50))
    
    try:
        print(f"   📧 Fetching up to {limit} recent emails...")
        
        # Get access token
        token = _get_graph_access_token()
        if not token:
            return json.dumps({
                "error": "Failed to obtain access token. Check MS_CLIENT_ID and MS_AUTHORITY."
            })
        
        # Query Microsoft Graph API for emails
        emails = _fetch_emails_from_graph(token, limit)
        
        if not emails:
            return "📧 No unread emails found."
        
        # Format output
        lines = [f"📧 Recent Emails ({len(emails)}):"]
        for i, email in enumerate(emails, 1):
            sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
            subject = email.get("subject", "(No subject)")
            lines.append(f"   {i}. From: {sender} | Subject: {subject}")
        
        print(f"   ✅ Retrieved {len(emails)} emails")
        return "\n".join(lines)
        
    except Exception as e:
        error_msg = f"Error fetching emails: {type(e).__name__}: {e}"
        print(f"   ❌ {error_msg}")
        return json.dumps({"error": error_msg})


def _get_graph_access_token() -> Optional[str]:
    """
    Obtain an access token for Microsoft Graph API using MSAL.
    
    Uses device code flow for interactive authentication if cached tokens
    are not available.
    
    Returns:
        Access token string or None if authentication fails.
    """
    if not MSAL_AVAILABLE:
        return None
    
    # Create MSAL public client application
    app = msal.PublicClientApplication(
        client_id=settings.MS_CLIENT_ID,
        authority=settings.MS_AUTHORITY
    )
    
    # Parse scopes from config
    scopes = [s.strip() for s in settings.MS_SCOPES.split(",")]
    # Ensure we have the proper Graph API scope format
    graph_scopes = []
    for scope in scopes:
        if not scope.startswith("https://"):
            graph_scopes.append(f"https://graph.microsoft.com/{scope}")
        else:
            graph_scopes.append(scope)
    
    # Try to get token from cache first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(graph_scopes, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]
            
    # Attempt Interactive Browser Auth first (better UX)
    print("   🔐 Attempting interactive browser authentication...")
    try:
        result = app.acquire_token_interactive(scopes=graph_scopes)
        if result and "access_token" in result:
            print("   ✅ Interactive authentication successful")
            return result["access_token"]
    except Exception as e:
        print(f"   ⚠️ Interactive auth failed/unavailable: {e}")
        print("   🔄 Falling back to Device Code flow...")
    
    # If interactive fails, use device code flow
    print("   🔐 Initiating device code authentication...")
    print("       (Follow the instructions to authenticate)")
    
    flow = app.initiate_device_flow(scopes=graph_scopes)
    if "user_code" not in flow:
        print(f"   ❌ Could not initiate device flow: {flow.get('error_description', 'Unknown error')}")
        return None
    
    print(f"   📋 {flow['message']}")
    
    # Wait for user to complete authentication
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        print("   ✅ Authentication successful")
        return result["access_token"]
    else:
        print(f"   ❌ Authentication failed: {result.get('error_description', 'Unknown error')}")
        return None


def _fetch_emails_from_graph(token: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch emails from Microsoft Graph API.
    
    Args:
        token: Valid access token for Graph API
        limit: Maximum number of emails to fetch
        
    Returns:
        List of email objects from Graph API
    """
    import requests
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Query for unread messages, ordered by received date
    endpoint = (
        f"https://graph.microsoft.com/v1.0/me/messages"
        f"?$filter=isRead eq false"
        f"&$orderby=receivedDateTime desc"
        f"&$top={limit}"
        f"&$select=subject,from,receivedDateTime,bodyPreview"
    )
    
    response = requests.get(endpoint, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return data.get("value", [])


def get_email_body(message_id: str) -> str:
    """Get the full body content of a specific email.
    
    Retrieves the complete email body for detailed reading.
    
    Args:
        message_id: The Microsoft Graph message ID
        
    Returns:
        The email body content as plain text or HTML.
    """
    if not MSAL_AVAILABLE:
        return json.dumps({"error": "MSAL library not installed"})
    
    try:
        token = _get_graph_access_token()
        if not token:
            return json.dumps({"error": "Authentication failed"})
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        body = data.get("body", {})
        
        return json.dumps({
            "subject": data.get("subject"),
            "from": data.get("from", {}).get("emailAddress", {}).get("address"),
            "received": data.get("receivedDateTime"),
            "body_type": body.get("contentType"),
            "body": body.get("content", "")[:2000]  # Limit body size
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})
