"""
Settings
"""

from datetime import datetime
import json
from functools import lru_cache
from pydantic_settings import BaseSettings
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest

from google.oauth2.credentials import Credentials
from google.auth.credentials import TokenState
from ..settings import get_redis_client


class GoogleAuthSettings(BaseSettings):
    """Google auth settings"""

    google_scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    google_redirect_url: str = "http://localhost:8000/google/redirect"
    google_credentials_filepath: str = "./credentials.json"
    google_token_key: str = "google_oauth_token"


@lru_cache
def get_google_settings():
    """Return google settings object"""
    return GoogleAuthSettings()


async def get_google_client() -> Credentials:
    """
    Retrieves the OAuth2 token from Redis and returns Google credentials.
    If the token is expired and a refresh token is available, it refreshes the token.
    If no token is found, an exception is raised.
    """
    token_json = await get_redis_client().get(get_google_settings().google_token_key)
    if not token_json:
        raise Exception("No token found. Please login via the /login endpoint.")
    credentials = Credentials(**json.loads(token_json))
    credentials.expiry = datetime.fromisoformat(credentials.expiry).replace(tzinfo=None)
    if (
        credentials.token_state in (TokenState.INVALID, TokenState.STALE)
        and credentials.refresh_token
    ):
        credentials.refresh(GoogleRequest())
        await get_redis_client().set(
            get_google_settings().google_token_key, credentials.to_json()
        )

    return credentials


@lru_cache
def get_google_flow():
    """Get authorized google client"""
    settings = get_google_settings()
    return Flow.from_client_secrets_file(
        settings.google_credentials_filepath,
        scopes=settings.google_scopes,
        redirect_uri=settings.google_redirect_url,
    )


class GmailFetchSettings(BaseSettings):
    """gmail fetch settings"""

    excluded_extensions: list[str] = [".exe", ".bat", ".ics"]
    max_results_per_page: int = 500
    fetch_limit: int = -1  # Set to -1 for unlimited processing
    api_uri: str = "http://localhost:8000"
    max_concurrent_emails: int = 20


@lru_cache
def get_gmail_fetch_settings():
    """Gmail fetch settings"""
    return GmailFetchSettings()


class DriveFetchSettings(BaseSettings):
    """Drive fetch settings"""

    excluded_extensions: list[str] = [".exe", ".bat", ".tmp"]
    max_concurrent_downloads: int = 20
    page_size: int = 100
    query: str = (
        "'me' in owners and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    )
    api_uri: str = "http://localhost:8000"


@lru_cache
def get_drive_fetch_settings():
    """Return drive fetch settings"""
    return DriveFetchSettings()
