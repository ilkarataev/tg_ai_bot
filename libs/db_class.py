from ast import Index
from datetime import datetime
from email.policy import default
from xmlrpc.client import Boolean, DateTime
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime,Boolean, Text, ForeignKey,Index, true
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# class Dialogs(Base):
#     __tablename__ = "dialogs"
#     id = Column(Integer, primary_key=True)
#     dialog_name = Column(String(255), unique=True, nullable=False, index=true)
#     text = Column(String(500), nullable=False)
class Photos(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String(255), nullable=False, index=true)
    photo = Column(LargeBinary(length=(2**32)-1), nullable=False)
    record_date = Column(DateTime, nullable=False,index=true)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String(50), nullable=False,index=true)
    notice = Column(Text(50))
    record_date = Column(DateTime, nullable=False)
    paid = Column(Boolean,default=False,index=true)