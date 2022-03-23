from typing import Optional, Union, Dict, Any

from sqlalchemy.orm import Session

from app.db.repository import CRUDBase
from .models import User, Email
from app.utils.security import lazy_jwt_settings


def convert_user_data(data: dict) -> dict:
    if data.get('password'):
        hashed_password = lazy_jwt_settings.JWT_PASSWORD_HANDLER(data["password"])
        del data["password"]
        data["hashed_password"] = hashed_password
    return data


class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: Union[dict,], ) -> Optional[User]:
        data_in = convert_user_data(obj_in)
        db_obj = self.model(**data_in)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user_db: User = self.get_by_email(db, email=email, )
        if not user_db:
            return None
        check_pass = lazy_jwt_settings.JWT_PASSWORD_VERIFY(password, user_db.hashed_password)
        if not check_pass:
            return None
        return user_db

    def update(
            self, db: Session,
            *,
            db_obj: User,
            obj_in: Dict[str, Any],
    ) -> User:
        data_in = convert_user_data(obj_in)
        return super().update(db, db_obj=db_obj, obj_in=data_in)


class CRUDEmail(CRUDBase[Email]):
    pass


user_repo = CRUDUser(User)
email_repo = CRUDEmail(Email)
