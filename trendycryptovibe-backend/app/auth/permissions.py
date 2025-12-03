from fastapi import Depends, HTTPException
from app.auth.jwt_handler import get_current_user

def admin_required(current_user=Depends(get_current_user)):
    roles = [role.name for role in current_user.roles]
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user