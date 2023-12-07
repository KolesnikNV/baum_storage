from sqlalchemy import Column, DateTime, Float, Integer, MetaData, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from utils.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(sessionmaker(bind=engine))
metadata = MetaData()
Base = declarative_base()


class MessageModel(Base):
    __tablename__ = "message_model"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, nullable=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=Float)


def create_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db()
