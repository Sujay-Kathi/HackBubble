import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.session import get_db
from app.models.user import User, UserProfile
from app.schemas.common import APIResponse
from app.schemas.user import (
    ProfileBootstrapRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    stmt = select(User).where(User.email == req.email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise ConflictError(message="A user with this email address already exists")

    user_id = uuid.uuid4()
    auth_subject = f"local|{user_id}"
    hashed_pwd = get_password_hash(req.password)

    user = User(
        id=user_id,
        email=req.email,
        auth_subject=auth_subject,
        hashed_password=hashed_pwd,
        account_status="active",
    )
    db.add(user)

    # Initialize empty profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        display_name=req.display_name,
        profile_visibility="public",
        resume_sharing="leaders_only",
    )
    db.add(profile)

    await db.commit()

    token = create_access_token(subject=str(user_id), claims={"email": req.email})
    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user_id,
            email=req.email,
        ),
        message="Registration successful",
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not user.hashed_password:
        raise UnauthorizedError(message="Invalid email or password")

    if not verify_password(req.password, user.hashed_password):
        raise UnauthorizedError(message="Invalid email or password")

    token = create_access_token(subject=str(user.id), claims={"email": user.email})
    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
        ),
        message="Login successful",
    )


@router.post("/profile/bootstrap", response_model=APIResponse[UserProfileResponse])
async def bootstrap_profile(
    req: ProfileBootstrapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
    )
    profile = (await db.execute(stmt)).scalar_one_or_none()

    if profile:
        profile.display_name = req.display_name
        if req.bio is not None:
            profile.bio = req.bio
        if req.location is not None:
            profile.location = req.location
        if req.domains_of_interest:
            profile.domains_of_interest = req.domains_of_interest
        if req.roles_of_interest:
            profile.roles_of_interest = req.roles_of_interest
    else:
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=current_user.id,
            display_name=req.display_name,
            bio=req.bio,
            location=req.location,
            domains_of_interest=req.domains_of_interest,
            roles_of_interest=req.roles_of_interest,
            profile_visibility="public",
            resume_sharing="leaders_only",
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)

    # Return refreshed profile data
    return APIResponse(
        success=True,
        data=UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            display_name=profile.display_name,
            bio=profile.bio,
            education_summary=profile.education_summary,
            location=profile.location,
            domains_of_interest=profile.domains_of_interest,
            roles_of_interest=profile.roles_of_interest,
            profile_visibility=profile.profile_visibility,
            resume_sharing=profile.resume_sharing,
            skills=[],
            projects=[],
            experience=[],
            achievements=[],
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        ),
        message="Profile bootstrapped successfully",
    )
