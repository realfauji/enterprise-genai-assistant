from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user


def require_role(required_role: str):
    async def role_dependency(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        return current_user
    return role_dependency