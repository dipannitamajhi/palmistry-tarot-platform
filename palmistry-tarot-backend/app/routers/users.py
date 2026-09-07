import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.reading import Reading
from app.schemas.user import UserOut, UserProfileUpdate
from app.schemas.reading import ReadingOut
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.put("/me", response_model=UserOut)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # .model_dump(exclude_unset=True) gives us only the fields the client
    # actually sent — so if they only send {"age_group": "25-34"}, we don't
    # accidentally overwrite name or interests with None.
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/readings", response_model=list[ReadingOut])
def get_my_reading_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Reading)
        .filter(Reading.user_id == current_user.id)
        .order_by(Reading.created_at.desc())
        .all()
    )

    # `details` is stored as a JSON string in the database (see the Reading
    # model). We parse it back into a real object here so the frontend
    # receives structured JSON, not a JSON-string-inside-JSON.
    results = []
    for row in rows:
        results.append(
            ReadingOut(
                id=row.id,
                reading_type=row.reading_type,
                summary=row.summary,
                details=json.loads(row.details),
                created_at=row.created_at,
            )
        )
    return results
