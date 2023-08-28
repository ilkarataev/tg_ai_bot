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
    Name = Column(String(50), nullable=True,index=true)
    Surname = Column(String(50), nullable=True,index=true)
    email = Column(String(50), nullable=True,index=true)
    tg_user_id = Column(String(50), nullable=False,index=true)
    clip_name = Column(String(50), nullable=False,index=true)
    record_date = Column(DateTime, nullable=False)
    notice = Column(Text(50))
    status = Column(String(50), nullable=True,index=true)
    render_host = Column(String(50), nullable=True,index=true)
    render_time = Column(Integer(), nullable=True,index=true)
    render_counter = Column(Integer(), nullable=True,index=true)

class render_hosts(Base):
    __tablename__ = "render_hosts"
    id = Column(Integer, primary_key=True)
    render_host = Column(String(50), nullable=True,unique=True,index=true)
    network_status = Column(String(50), nullable=True,index=true)
    record_date = Column(DateTime, nullable=False)
    render_enabled = Column(Boolean, server_default='1', nullable=True)

class video_clips(Base):
    __tablename__ = "video_clips"
    id = Column(Integer, primary_key=True)
    name_ru = Column(String(50), nullable=True,index=true)
    name_en = Column(String(50), nullable=True,index=true,unique=True)
    url= Column(String(800), nullable=True,index=False)
    path= Column(String(500), nullable=True,index=True)
    md5= Column(String(500), nullable=True,index=True)
    category = Column(String(80), nullable=True,index=True)

class paid(Base):
    __tablename__ = "paid"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String(50), nullable=False,index=true)
    paid_date = Column(DateTime, nullable=False,index=true)