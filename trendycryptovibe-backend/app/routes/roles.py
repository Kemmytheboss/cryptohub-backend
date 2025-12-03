from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.role import Role
from app.models.user import User
from app.auth.jwt_handler import get_current_user
from app.auth.permissions import admin_required

router = APIRouter(prefix="/roles", tags=["Roles"])

# admin only endpoint to create roles
@router.post("/create")
def create_role(
    role_name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not authorized to create roles")

    existing_role = db.query(Role).filter(Role.name == role_name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

        role = Role(name=role_name)
    db.add(role)
    db.commit()
    return {"message": f"Role '{role_name}' created successfully"}

# endpoint to assign role to user
@router.post("/assign")
def assign_role_to_user(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not authorized to assign roles")

    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.name == role_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == role_name).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        raise HTTPException(status_code=400, detail="User already has this role")

    user.roles.append(role)
    db.commit()
    return {"message": f"Role '{role_name}' assigned to user ID {user_id} successfully"}