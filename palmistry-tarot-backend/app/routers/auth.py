from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        # Public registration must never be able to mint a staff or admin account.
        # A deployment administrator can assign staff roles through a controlled
        # back-office workflow or database migration.
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # pulls back the auto-generated id and created_at
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Deliberately vague error message: we don't reveal whether the email
    # exists or the password was wrong. That distinction helps attackers
    # enumerate valid accounts.
    invalid_credentials = HTTPException(status_code=401, detail="Incorrect email or password.")

    if not user or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, user=user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    # Demonstrates the get_current_user dependency: this endpoint has no
    # idea who's asking until the dependency decodes their JWT for us.
    return current_user
