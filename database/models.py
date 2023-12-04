from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey

DB_HOST = "uni_task-bd-1"
# DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"

DATABASE_URL = (f"postgresql://{DB_USER}:{DB_PASS}"
                f"@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(DATABASE_URL)

"""SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)"""


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    biography = Column(String)
    books = relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan"
        )


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False, )
    author = relationship("Author", back_populates="books")
    book_title = Column(String, nullable=False)
    description = Column(String)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
