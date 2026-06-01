from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app.repository import UserRepository

security = HTTPBearer()


def get_current_user(
    user_repo: UserRepository,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token")

    user = user_repo.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(401, "User not found")

    return user
