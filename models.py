from datetime import date

from sqlalchemy import create_engine, String, Integer, ForeignKey, Table, Column, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


engine = create_engine("sqlite:///library.db", echo=False)


class Base(DeclarativeBase):
    pass


# Many-to-many association table
book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(200))

    bio: Mapped[str | None] = mapped_column(String(200), nullable=True)

    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="authors"
    )


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(200))

    email: Mapped[str] = mapped_column(String(200), unique=True)

    membership_date: Mapped[date] = mapped_column(Date)

    borrowings: Mapped[list["Borrowing"]] = relationship(
        back_populates="member"
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(200))

    isbn: Mapped[str] = mapped_column(String(200), unique=True)

    year_published: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    available_copies: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors,
        back_populates="books"
    )

    borrowings: Mapped[list["Borrowing"]] = relationship(
        back_populates="book"
    )


class Borrowing(Base):
    __tablename__ = "borrowings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id")
    )

    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id")
    )

    checkout_date: Mapped[date] = mapped_column(Date)

    return_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    book: Mapped["Book"] = relationship(
        back_populates="borrowings"
    )

    member: Mapped["Member"] = relationship(
        back_populates="borrowings"
    )


def init_db():
    Base.metadata.create_all(engine)