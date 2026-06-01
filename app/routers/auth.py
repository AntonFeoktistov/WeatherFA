from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.repository import UserRepository
from app.schemas import UserLogin, UserSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserSchema, db: Session = Depends(get_db)):
    existing = user_repo.get_user_by_name(db, user_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists",
        )

    hashed_password = hash_password(user_data.password1)
    user_repo.create_user(db, user_data.name, hashed_password)
    db.commit()

    return {"message": "User created successfully", "username": user_data.name}


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_name(db, user_data.username)

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
