from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    surname = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    token = Column(String(36), nullable=False)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False)
    content = Column(String(5012), nullable=False)
    is_private = Column(Boolean, default=False)
    image_uuid = Column(String(36), nullable=True)
    author_id = Column(Integer, ForeignKey('user.id'))


engine = create_engine('postgresql+psycopg2://wad-adm:StrongPassw0rd@db:5432/wad_db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session(autocommit=True)  # type: sqlalchemy.orm.Session
