"""
Reusable FastAPI dependencies for authentication and role checks.

A "dependency" in FastAPI is just a function you can require any endpoint
to run first. get_current_user reads the JWT from the request, verifies
it, and looks up the matching user — so any endpoint that needs to know
"who is calling this?" just adds one parameter instead of repeating this
logic everywhere.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.security import decode_access_token

# This tells FastAPI's auto-generated docs (/docs) that clients should send
# a "Bearer <token>" header, and where they'd get that token from (login).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# A second scheme with auto_error=False: unlike the one above, this one
# doesn't raise an error when no token is present — it just returns None.
# That's what lets an endpoint behave differently for guests vs.
# logged-in users, instead of blocking guests outright.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_error

    return user


def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Same idea as get_current_user, but never raises. Used on endpoints
    like palm/tarot analysis that should work for anonymous visitors too —
    we just skip saving history if there's no valid user.
    """
    if token is None:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == int(user_id)).first()


def require_role(*allowed_roles: UserRole):
    """
    A dependency FACTORY: it returns a dependency customized with whichever
    roles you pass in. Usage on an endpoint:

        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMINISTRATOR))])

    This is how the doc's "Role-based access control" requirement (module 1)
    actually gets enforced, not just stored as a label on the user.
    """
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return dependency
