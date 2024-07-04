from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

url = "postgresql://postgres:postgres@localhost/prak"
Base = declarative_base()
engine = create_engine(url)
Session = sessionmaker(engine)
session = Session()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(String, primary_key=True, unique=True)
    title = Column(String)
    experience = Column(String)
    link = Column(String)
    company = Column(String)
    salary = Column(String)
    location = Column(String)


Base.metadata.create_all(engine)
