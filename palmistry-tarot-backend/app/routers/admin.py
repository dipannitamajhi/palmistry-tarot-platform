from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.reading import Reading
from app.schemas.user import UserOut
from app.auth.dependencies import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_all_users(
    db: Session = Depends(get_db),
    # This single line is the "Admin Dashboard -> User management" feature
    # from the spec (section 4.10). Anyone whose token doesn't belong to
    # an Administrator gets a 403 automatically, before this code even runs.
    _admin: User = Depends(require_role(UserRole.ADMINISTRATOR)),
):
    return db.query(User).all()


class RoleUpdate(BaseModel):
    role: UserRole


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMINISTRATOR)),
):
    """Promote/demote a user between the four spec roles (User, Tarot
    Reader, Spiritual Consultant, Administrator). This is the missing
    half of 'Role-based access control' — the enum and enforcement
    already existed, but nothing let an admin actually assign a staff
    role. Only an Administrator can call this."""
    if user_id == admin.id and payload.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=400, detail="You can't demote your own account.")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMINISTRATOR)),
):
    """Remove a user account. Part of Admin Dashboard -> User management."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You can't delete your own account.")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    db.query(Reading).filter(Reading.user_id == user_id).delete()
    db.delete(user)
    db.commit()