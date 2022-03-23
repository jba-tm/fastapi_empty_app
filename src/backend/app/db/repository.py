from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, TYPE_CHECKING

from fastapi.encoders import jsonable_encoder

from .models import Base
from app.conf.config import settings

ModelType = TypeVar("ModelType", bound=Base)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CRUDBase(Generic[ModelType,]):
    def __init__(self, model: Type[ModelType], ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def count(self, db: "Session", *, q: Optional[dict] = None, **kwargs):
        if q is None:
            q = {}
        return db.query(self.model).filter_by(**q).count()

    def get_by_params(self, db: "Session", params: dict, ) -> Optional[ModelType]:
        """
        Retrieve items by params
        :param db:
        :param params:
        :return:
        """
        return db.query(self.model).filter_by(**params).first()

    def get_all(
            self, db: "Session", *, offset: Optional[int] = 0, limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
            q: Optional[dict] = None, order_by: Optional[list] = None,
            **kwargs,
    ) -> Union[List[ModelType], Any]:
        """

        :param db:
        :param offset:
        :param limit:
        :param q:
        :param order_by:
        :param kwargs:
        :return:
        """
        if order_by is None:
            order_by = []
        if q is None:
            q = {}
        return db.query(self.model).order_by(*order_by).filter_by(**q).offset(offset).limit(limit).all()

    def create(self, db: "Session", *, obj_in: Union[Dict[str, Any]]) -> ModelType:
        """
        Create item
        :param db:
        :param obj_in:
        :return:
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: "Session",
            *,
            db_obj: ModelType,
            obj_in: Union[Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, )
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: "Session", *,
               db_obj: ModelType,
               ) -> ModelType:
        """
        Delete item
        :param db_obj:
        :param db:
        :return:
        """
        db.delete(db_obj)
        db.commit()
        return db_obj
