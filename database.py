from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(String(100), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    goal = Column(String(60), nullable=False)
    intensity = Column(String(30), nullable=False)
    workout_plan = Column(Text, nullable=False)
    nutrition_tip = Column(Text, nullable=False)
    feedback = Column(Text, default="")
    updated_plan = Column(Text, default="")


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()