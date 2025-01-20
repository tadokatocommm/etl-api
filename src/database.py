from sqlalchemy import Column, String, Integer, DateTime, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CasosCovid(Base):  
    __tablename__ = "casos_covid" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    pais = Column(String, nullable=False)
    data = Column(String, nullable=False)
    vacinas_aplicadas = Column(BigInteger, nullable=False)  
    timestamp = Column(DateTime, nullable=False)
