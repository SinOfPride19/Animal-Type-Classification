from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    animal = Column(String(50))
    score = Column(Float)
    grade = Column(String(50))