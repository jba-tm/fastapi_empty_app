from app.db.repository import CRUDBase

from .models import Post


class CRUDPost(CRUDBase[Post]):
    pass


post_repo = CRUDPost(Post)
