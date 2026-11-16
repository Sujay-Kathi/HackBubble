import uuid
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not auth or not auth.credentials:
        raise UnauthorizedError(message="Authentication token missing")

    token = auth.credentials
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError(message="Invalid token payload: missing sub")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        # Fallback if sub is auth_subject string
        stmt = (
            select(User)
            .where(User.auth_subject == user_id_str)
            .options(
                selectinload(User.profile),
                selectinload(User.skills),
                selectinload(User.projects),
                selectinload(User.experience),
                selectinload(User.achievements),
            )
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError(message="User account not found")
        return user

    stmt = (
        select(User)
        .where(User.id == user_id)
        .execution_options(populate_existing=True)
        .options(
            selectinload(User.profile),
            selectinload(User.skills),
            selectinload(User.projects),
            selectinload(User.experience),
            selectinload(User.achievements),
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError(message="User account not found")
    if user.account_status != "active":
        raise ForbiddenError(message="User account is suspended or inactive")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Reject non-administrators from privileged endpoints."""
    if not current_user.is_admin:
        raise ForbiddenError(message="Administrator privileges required")
    return current_user


async def get_optional_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not auth or not auth.credentials:
        return None
    try:
        return await get_current_user(auth, db)
    except Exception:
        return None
