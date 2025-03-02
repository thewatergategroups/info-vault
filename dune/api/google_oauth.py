"""
google oauth2 router
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from ..settings import (
    get_redis_client,
)
from ..google.settings import (
    get_google_flow,
    get_google_settings,
    get_google_client,
)

router = APIRouter(prefix="/google", tags=["google oauth endpoints"])


@router.get("/login")
async def login():
    """
    Initiates the OAuth2 flow. Redirects the user to Google’s authorization URL.
    """
    auth_url, _ = get_google_flow().authorization_url(
        prompt="consent", access_type="offline"
    )
    return RedirectResponse(auth_url)


@router.get("/redirect")
async def oauth2callback(code: str):
    """
    Callback endpoint for Google OAuth2. Exchanges the authorization code for tokens
    and stores them in Redis.
    """
    get_google_flow().fetch_token(code=code)
    await get_redis_client().set(
        get_google_settings().google_token_key,
        get_google_flow().credentials.to_json(),
    )
    return HTMLResponse("Authorization successful. You can close this window.")


# Example endpoint to demonstrate usage of get_client()
@router.get("/profile")
async def profile():
    """
    Example endpoint that uses the stored credentials to access a Google API.
    (For instance, you could use it to get the user's profile information.)
    """
    try:
        credentials = await get_google_client()
    except Exception as e:
        logging.exception("failed to get creds")
        raise HTTPException(status_code=401, detail=str(e))

    # Here you would normally create an API client (e.g., for Gmail or Drive)
    # and make API calls using the authorized credentials.
    # For simplicity, we'll just return a message.
    return {"message": "Token is valid", "token": credentials.token}
