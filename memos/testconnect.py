


from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://memosystem:memopw@localhost:3306/memos', echo = True)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Customers(Base):
   __tablename__ = 'customers'
   id = Column(Integer, primary_key=True)
   num = Column(Integer)

Base.metadata.create_all(engine)

