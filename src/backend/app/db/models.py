import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):
    __name__: str
    id = sa.Column(sa.Integer, primary_key=True, index=True, )

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}'
