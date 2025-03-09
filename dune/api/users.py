"""
Defining User information and schemas
"""

from functools import lru_cache
import uuid
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import schemas, BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.authentication.strategy.jwt import JWTStrategy

from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from ..database.models import User, OAuthAccount, AccessToken
from ..settings import get_async_session, get_user_settings


@lru_cache
def get_google_oauth_client():
    """Cached google oauth2 client"""
    return GoogleOAuth2(
        get_user_settings().google_client_id, get_user_settings().google_client_secret
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """User db fetcher"""
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):
    """access token db"""
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    """Access token strategy with db backend"""
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    """return jwt strategy"""
    return JWTStrategy(secret=get_user_settings().user_pw_secret, lifetime_seconds=3600)


class UserRead(schemas.BaseUser[uuid.UUID]):
    """User read model"""


class UserCreate(schemas.BaseUserCreate):
    """User create model"""


class UserUpdate(schemas.BaseUserUpdate):
    """User update model"""


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager class"""

    reset_password_token_secret = get_user_settings().user_pw_secret
    verification_token_secret = get_user_settings().user_pw_secret

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """yield user manager"""
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_name="docsid")


bearer_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [bearer_backend, cookie_backend]
)

current_active_user = fastapi_users.current_user(active=True)
