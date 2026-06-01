from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Location, User


class UserRepository:
    def __init__(self):
        pass

    def get_user_by_name(self, session: Session, name: str):
        stmt = select(User).where(User.name == name)
        return session.scalars(stmt).first()

    def get_user_by_id(self, session: Session, id: int):
        stmt = select(User).where(User.id == id)
        return session.scalars(stmt).first()

    def create_user(self, session: Session, name: str, hashed_password: str):
        new_user = User(name=name, hashed_password=hashed_password)
        session.add(new_user)
        session.flush()
        return new_user


class LocationRepository:
    def __init__(self):
        pass

    def get_all_by_user_id(self, session: Session, id: int):
        stmt = select(Location).where(user_id=id)
        return session.scalars(stmt).all()
