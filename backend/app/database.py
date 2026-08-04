from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings # Day la import settings tu file config.py

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Tao session local tu engine voi tuy chon khong autocommit va khong autoflush
Base = declarative_base() # Ham declarative_base() tao ra mot lop co so de khai bao cac model cua SQLAlchemy

def get_db():
    db = SessionLocal()
    try:
        yield db # yield la mot tu khoa trong Python dung de tao ra mot generator. Khi ham get_db() duoc goi, no se tra ve mot doi tuong db (mot session cua SQLAlchemy) va cho phep cac ham khac su dung doi tuong db nay de truy cap co so du lieu. Khi ket thuc, no se dong session db.
    finally:
        db.close()