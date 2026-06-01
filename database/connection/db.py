import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()


class DB:
    def __init__(self):
        url = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('APP_HOST')}:"
            f"{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}"
        )

        self.engine = create_engine(url, pool_pre_ping=True)

        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def session(self):
        return self.Session()


db = DB()
Base = declarative_base()
