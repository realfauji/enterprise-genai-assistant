from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.dependencies import get_db
from app.models.user import User
from app.models.schemas import UserCreate, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

from app.core.security import get_current_user
from app.middleware.rbac import require_role


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data:UserCreate, db:AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="user"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

@router.get("/me")
async def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id, "email": current_user.email, "role": current_user.role}

@router.get("/admin-only")
async def admin_route(current_user=Depends(require_role("admin"))):
    return {"message": "Welcome Admin"}