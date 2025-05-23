"""
Create the FastApi application.
"""

from urllib.parse import quote

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse

from .routers.docs import router as docrouter
from .routers.chat import router as chatrouter
from .users import (
    UserUpdate,
    UserCreate,
    UserRead,
    fastapi_users,
    bearer_backend,
    cookie_backend,
    get_google_oauth_client,
)
from ..settings import get_user_settings


def create_app() -> FastAPI:
    """
    create and return fastapi app
    """
    app = FastAPI(
        title="Document Parser",
        description="Parses Documents",
        version="1.0",
    )

    @app.middleware("http")
    async def _(request: Request, call_next):
        """redirect to home page after auth callback"""
        response: Response = await call_next(request)
        if "callback" in request.url.path:
            response.status_code = 302
            response.headers["location"] = quote(
                "http://localhost:5173/#/chat", safe=":/%#?=@[]!$&'()*+,;"
            )
        return response

    routers = [docrouter, chatrouter]
    for router in routers:
        app.include_router(router)

    app.include_router(
        fastapi_users.get_auth_router(bearer_backend), prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_auth_router(cookie_backend),
        prefix="/auth/cookie",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
    app.include_router(
        fastapi_users.get_oauth_router(
            get_google_oauth_client(),
            bearer_backend,
            get_user_settings().user_pw_secret,
            associate_by_email=True,
        ),
        prefix="/auth/jwt/google",
        tags=["bearer token auth"],
    )
    app.include_router(
        fastapi_users.get_oauth_router(
            get_google_oauth_client(),
            cookie_backend,
            get_user_settings().user_pw_secret,
            associate_by_email=True,
        ),
        prefix="/auth/cookie/google",
        tags=["cookie auth"],
    )

    return app
