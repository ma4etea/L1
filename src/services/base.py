from src.utils.db_manager import DBManager

# todo возможно для супер продакшен реди, нужно в сервис передовать дата классы или дикт а не педантик схемы(в сервисе должен быть только пайтон)
class BaseService:
    db: DBManager | None
    def __init__(self, db: DBManager | None = None):
        self.db = db