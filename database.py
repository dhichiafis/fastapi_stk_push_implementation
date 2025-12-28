from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker,Session ,declarative_base


url="sqlite:///fourth.db"
Base=declarative_base()
engine=create_engine(url=url)

SessionFactory=sessionmaker(bind=engine,autoflush=False,autocommit=False)


def connect():
    db=SessionFactory()
    try:
        yield db 
    finally:
        db.close()