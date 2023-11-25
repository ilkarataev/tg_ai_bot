from ast import Index
from datetime import datetime
from email.policy import default
from xmlrpc.client import Boolean, DateTime
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime,Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base,relationship


Base = declarative_base()
class photos(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String(255), nullable=False, index=True)
    photo = Column(LargeBinary(length=(2**32)-1), nullable=False)
    record_date = Column(DateTime, nullable=False,index=True)

class users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True,index=True)
    surname = Column(String(50), nullable=True,index=True)
    email = Column(String(50), nullable=True,index=True)
    tg_user_id = Column(BigInteger, nullable=False,index=True)
    photo = Column(LargeBinary(length=(2**32)-1), nullable=True)
    clip_name = Column(String(50), nullable=True,index=True)
    record_date = Column(DateTime, nullable=True)
    notice = Column(Text(50))
    status = Column(String(50), nullable=True,index=True)
    render_host = Column(String(50), nullable=True,index=True)
    render_time = Column(Integer(), nullable=True,index=True)
    render_counter = Column(Integer(), nullable=True,index=True)
    final_clip_size = Column(Integer(), nullable=True,index=True)

class tg_users(Base):
    __tablename__ = "tg_users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True,index=True)
    surname = Column(String(50), nullable=True,index=True)
    email = Column(String(50), nullable=True,index=True)
    username = Column(String(50), nullable=True,index=True)
    language_code = Column(String(50), nullable=True,index=True)
    tg_user_id = Column(BigInteger, nullable=False,unique=True,index=True)
    reg_date = Column(DateTime, nullable=False)
    bots = relationship('tg_bot', back_populates='user')

    def __repr__(self):
            return f"{self.name}, tg_user_id={self.tg_user_id}"

class tg_bot(Base):
    __tablename__ = "tg_bot"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BigInteger, ForeignKey('tg_users.tg_user_id'), nullable=False, index=True)
    bot_step = Column(String(50), nullable=True,index=True)
    step_date = Column(DateTime, nullable=False)
    user = relationship('tg_users', back_populates='bots')

class render_hosts(Base):
    __tablename__ = "render_hosts"
    id = Column(Integer, primary_key=True)
    render_host = Column(String(50), nullable=True,unique=True,index=True)
    network_status = Column(String(50), nullable=True,index=True)
    record_date = Column(DateTime, nullable=False)
    render_enabled = Column(Boolean, server_default='1', nullable=True)

class video_clips(Base):
    __tablename__ = "video_clips"
    id = Column(Integer, primary_key=True)
    name_ru = Column(String(50), nullable=True,index=True)
    name_en = Column(String(50), nullable=True,index=True,unique=True)
    url= Column(String(500), nullable=True,index=True,unique=True)
    path= Column(String(500), nullable=True,index=True)
    md5= Column(String(500), nullable=True,index=True)
    category = Column(String(80), nullable=True,index=True)

class payments(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BigInteger, nullable=False,index=True)
    payments_date = Column(DateTime, nullable=False,index=True)

class logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    log = Column(String(500), nullable=False,index=True)