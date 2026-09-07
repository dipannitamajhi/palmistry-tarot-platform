import json

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from app.services.palm_analysis import analyze_palm_image
from app.database import get_db
from app.models.user import User
from app.models.reading import Reading, ReadingType
from app.auth.dependencies import get_optional_current_user
from app.services.insights import build_interpretation
from app.services.notifications import notify_reading_ready


router = APIRouter(
    prefix="/api/palm",
    tags=["palm"],
)


@router.post("/analyze")
async def analyze_palm(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
):

    if image.content_type not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPEG, PNG, or WebP image.",
        )

    contents = await image.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image must be 10 MB or smaller.",
        )

    try:

        result = analyze_palm_image(
            contents
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    result["interpretation"] = build_interpretation(
        "palm",
        result,
        current_user,
    )

    if current_user:

        reading = Reading(
            user_id=current_user.id,
            reading_type=ReadingType.PALM,
            summary=(
                f"Palm reading "
                f"(confidence {result['confidence']})"
            ),
            details=json.dumps(result),
        )

        db.add(reading)
        db.commit()

        notify_reading_ready(
            db,
            current_user,
            "palm",
        )

    return result