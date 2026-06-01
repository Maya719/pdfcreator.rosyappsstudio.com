from database.connection.db import db


class BaseModel:
    @classmethod
    def query(cls):
        return db.session().query(cls)
