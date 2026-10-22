from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import engine, Book, Author, Member, Borrowing


def add_book(
    title: str,
    isbn: str,
    year_published: int = None,
    available_copies: int = 1
):
    """Add a new book to the library."""

    if not title.strip():
        raise ValueError("Book title cannot be empty")

    if not isbn.strip():
        raise ValueError("ISBN cannot be empty")

    if available_copies < 0:
        raise ValueError("Available copies cannot be negative")

    with Session(engine) as session:
        try:
            book = Book(
                title=title.strip(),
                isbn=isbn.strip(),
                year_published=year_published,
                available_copies=available_copies
            )

            session.add(book)
            session.commit()
            session.refresh(book)

            return book

        except IntegrityError:
            session.rollback()
            raise ValueError("A book with that ISBN already exists")


def add_author(name: str, bio: str = None):
    """Add a new author to the library."""

    if not name.strip():
        raise ValueError("Author name cannot be empty")

    with Session(engine) as session:
        try:
            author = Author(
                name=name.strip(),
                bio=bio
            )

            session.add(author)
            session.commit()
            session.refresh(author)

            return author

        except IntegrityError:
            session.rollback()
            raise ValueError("Could not add author")


def add_member(name: str, email: str):
    """Add a new member to the library."""

    if not name.strip():
        raise ValueError("Member name cannot be empty")

    if not email.strip():
        raise ValueError("Email cannot be empty")

    with Session(engine) as session:
        try:
            member = Member(
                name=name.strip(),
                email=email.strip(),
                membership_date=date.today()
            )

            session.add(member)
            session.commit()
            session.refresh(member)

            return member

        except IntegrityError:
            session.rollback()
            raise ValueError("A member with that email already exists")


def checkout_book(book_id: int, member_id: int):
    """Check out an available book to a library member."""

    with Session(engine) as session:
        try:
            book = session.get(Book, book_id)
            member = session.get(Member, member_id)

            if not book:
                raise ValueError("Book not found")

            if not member:
                raise ValueError("Member not found")

            if book.available_copies <= 0:
                raise ValueError("No copies available")

            existing_borrowing = session.scalar(
                select(Borrowing).where(
                    Borrowing.book_id == book_id,
                    Borrowing.member_id == member_id,
                    Borrowing.return_date.is_(None)
                )
            )

            if existing_borrowing:
                raise ValueError(
                    "This member already has this book checked out"
                )

            borrowing = Borrowing(
                book_id=book.id,
                member_id=member.id,
                checkout_date=date.today(),
                return_date=None
            )

            book.available_copies -= 1

            session.add(borrowing)
            session.commit()
            session.refresh(borrowing)

            return borrowing

        except ValueError:
            session.rollback()
            raise

        except IntegrityError:
            session.rollback()
            raise ValueError("Could not check out the book")


def list_books():
    """Return all books in the library."""

    with Session(engine) as session:
        return session.scalars(
            select(Book).order_by(Book.title)
        ).all()


def search_books_by_title(title: str):
    """Search for books whose titles contain the search text."""

    if not title.strip():
        return []

    with Session(engine) as session:
        return session.scalars(
            select(Book)
            .where(Book.title.ilike(f"%{title.strip()}%"))
            .order_by(Book.title)
        ).all()


def find_books_by_author(author_name: str):
    """Find all books written by an author."""

    if not author_name.strip():
        return []

    with Session(engine) as session:
        author = session.scalar(
            select(Author)
            .where(Author.name.ilike(f"%{author_name.strip()}%"))
        )

        if not author:
            return []

        return list(author.books)


def list_member_borrowings(member_id: int):
    """Return all currently borrowed books for a member."""

    with Session(engine) as session:
        member = session.get(Member, member_id)

        if not member:
            raise ValueError("Member not found")

        borrowings = session.scalars(
            select(Borrowing)
            .where(
                Borrowing.member_id == member_id,
                Borrowing.return_date.is_(None)
            )
            .order_by(Borrowing.checkout_date)
        ).all()

        return borrowings


def list_overdue_books(days: int = 14):
    """Return all unreturned books checked out longer than the given days."""

    if days < 0:
        raise ValueError("Days cannot be negative")

    cutoff = date.today() - timedelta(days=days)

    with Session(engine) as session:
        return session.scalars(
            select(Borrowing)
            .where(
                Borrowing.return_date.is_(None),
                Borrowing.checkout_date < cutoff
            )
            .order_by(Borrowing.checkout_date)
        ).all()


def return_book(borrowing_id: int):
    """Return a borrowed book and increase its available copy count."""

    with Session(engine) as session:
        try:
            borrowing = session.get(Borrowing, borrowing_id)

            if not borrowing:
                raise ValueError("Borrowing not found")

            if borrowing.return_date is not None:
                raise ValueError("Book already returned")

            borrowing.return_date = date.today()
            borrowing.book.available_copies += 1

            session.commit()
            session.refresh(borrowing)

            return borrowing

        except ValueError:
            session.rollback()
            raise

        except IntegrityError:
            session.rollback()
            raise ValueError("Could not return the book")


def update_member_email(member_id: int, new_email: str):
    """Update a member's email address."""

    if not new_email.strip():
        raise ValueError("Email cannot be empty")

    with Session(engine) as session:
        try:
            member = session.get(Member, member_id)

            if not member:
                raise ValueError("Member not found")

            member.email = new_email.strip()

            session.commit()
            session.refresh(member)

            return member

        except ValueError:
            session.rollback()
            raise

        except IntegrityError:
            session.rollback()
            raise ValueError("A member with that email already exists")


def delete_book(book_id: int):
    """Delete a book if it has no active borrowings."""

    with Session(engine) as session:
        try:
            book = session.get(Book, book_id)

            if not book:
                raise ValueError("Book not found")

            if any(
                borrowing.return_date is None
                for borrowing in book.borrowings
            ):
                raise ValueError("Book is currently borrowed")

            # Remove historical borrowing records before deleting
            # the book so foreign-key relationships remain valid.
            for borrowing in list(book.borrowings):
                session.delete(borrowing)

            session.delete(book)
            session.commit()

            return True

        except ValueError:
            session.rollback()
            raise

        except IntegrityError:
            session.rollback()
            raise ValueError("Could not delete the book")


def delete_member(member_id: int):
    """Delete a member if they have no active borrowings."""

    with Session(engine) as session:
        try:
            member = session.get(Member, member_id)

            if not member:
                raise ValueError("Member not found")

            if any(
                borrowing.return_date is None
                for borrowing in member.borrowings
            ):
                raise ValueError(
                    "Member has active borrowings"
                )

            # Remove historical borrowing records before deleting
            # the member so foreign-key relationships remain valid.
            for borrowing in list(member.borrowings):
                session.delete(borrowing)

            session.delete(member)
            session.commit()

            return True

        except ValueError:
            session.rollback()
            raise

        except IntegrityError:
            session.rollback()
            raise ValueError("Could not delete the member")