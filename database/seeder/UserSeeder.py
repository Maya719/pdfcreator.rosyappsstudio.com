from database.connection.db import db
from app.models.User import User
import bcrypt


class UserSeeder:
    def run(self):
        session = db.session()

        user = User(username="admin", password=hash_password("mobi@pdf"))

        session.add(user)
        session.commit()
        session.close()

        return "User seeded"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password[:72].encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password[:72].encode(), hashed.encode())
