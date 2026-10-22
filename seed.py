from datetime import date, timedelta

from models import engine, init_db, Book, Author, Member, Borrowing
from sqlalchemy.orm import Session


def seed():
    """Populate the database with sample library data."""

    init_db()

    with Session(engine) as session:
        # Create authors
        author1 = Author(
            name="George Orwell",
            bio="English novelist and essayist."
        )

        author2 = Author(
            name="Jane Austen",
            bio="English novelist known for her works of fiction."
        )

        author3 = Author(
            name="J.R.R. Tolkien",
            bio="English writer and creator of Middle-earth."
        )

        author4 = Author(
            name="Agatha Christie",
            bio="English writer known for mystery novels."
        )

        session.add_all([
            author1,
            author2,
            author3,
            author4
        ])

        session.flush()

        # Create books
        book1 = Book(
            title="1984",
            isbn="9780451524935",
            year_published=1949,
            available_copies=3
        )

        book2 = Book(
            title="Animal Farm",
            isbn="9780451526342",
            year_published=1945,
            available_copies=2
        )

        book3 = Book(
            title="Pride and Prejudice",
            isbn="9780141439518",
            year_published=1813,
            available_copies=3
        )

        book4 = Book(
            title="The Hobbit",
            isbn="9780547928227",
            year_published=1937,
            available_copies=4
        )

        book5 = Book(
            title="Murder on the Orient Express",
            isbn="9780062693662",
            year_published=1934,
            available_copies=2
        )

        # Connect books to authors
        book1.authors.append(author1)
        book2.authors.append(author1)
        book3.authors.append(author2)
        book4.authors.append(author3)
        book5.authors.append(author4)

        session.add_all([
            book1,
            book2,
            book3,
            book4,
            book5
        ])

        # Create members
        member1 = Member(
            name="Alice Johnson",
            email="alice@example.com",
            membership_date=date.today()
        )

        member2 = Member(
            name="Brian Smith",
            email="brian@example.com",
            membership_date=date.today()
        )

        member3 = Member(
            name="Carol Williams",
            email="carol@example.com",
            membership_date=date.today()
        )

        member4 = Member(
            name="David Brown",
            email="david@example.com",
            membership_date=date.today()
        )

        session.add_all([
            member1,
            member2,
            member3,
            member4
        ])

        session.flush()

        # Create 6 borrowings.
        # Some are active and some are returned.
        #
        # Two active borrowings are intentionally older than
        # 14 days so they can be detected as overdue.

        borrowing1 = Borrowing(
            book=book1,
            member=member1,
            checkout_date=date.today() - timedelta(days=30),
            return_date=None
        )

        borrowing2 = Borrowing(
            book=book2,
            member=member2,
            checkout_date=date.today() - timedelta(days=20),
            return_date=None
        )

        borrowing3 = Borrowing(
            book=book3,
            member=member3,
            checkout_date=date.today() - timedelta(days=5),
            return_date=None
        )

        borrowing4 = Borrowing(
            book=book4,
            member=member4,
            checkout_date=date.today() - timedelta(days=25),
            return_date=date.today() - timedelta(days=10)
        )

        borrowing5 = Borrowing(
            book=book5,
            member=member1,
            checkout_date=date.today() - timedelta(days=40),
            return_date=date.today() - timedelta(days=25)
        )

        borrowing6 = Borrowing(
            book=book4,
            member=member2,
            checkout_date=date.today() - timedelta(days=3),
            return_date=None
        )

        session.add_all([
            borrowing1,
            borrowing2,
            borrowing3,
            borrowing4,
            borrowing5,
            borrowing6
        ])

        # Adjust available copies based on currently active borrowings.
        book1.available_copies -= 1
        book2.available_copies -= 1
        book3.available_copies -= 1
        book4.available_copies -= 1

        session.commit()

    print("Seed complete!")
    print()
    print("Created:")
    print("- 4 authors")
    print("- 5 books")
    print("- 4 members")
    print("- 6 borrowings")
    print("- 2 returned borrowings")
    print("- 4 active borrowings")
    print("- 2 overdue borrowings")


if __name__ == "__main__":
    seed()