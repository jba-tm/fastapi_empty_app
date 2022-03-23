from app.db.repository import CRUDBase

from .models import Config


class CRUDConfig(CRUDBase[Config]):
    pass


config_repo = CRUDConfig(Config)
