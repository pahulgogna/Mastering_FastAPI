from sqlalchemy import Column,Integer,String,Boolean,Time
from database import Base

class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer,nullable=False,primary_key=True)
    title = Column(String,nullable=False)
    content = Column(String, nullable=False)
    Posted_by = Column(Integer,default=0,nullable=False)
    publish = Column(Boolean, nullable=False,default=True)