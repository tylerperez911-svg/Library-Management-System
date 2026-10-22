from models import init_db
from crud import (
    add_book,
    add_member,
    checkout_book,
    return_book,
    list_books,
    search_books_by_title,
    find_books_by_author,
    list_member_borrowings,
    list_overdue_books,
)


def get_integer(prompt, minimum=None):
    """Prompt the user for a valid integer."""
    while True:
        value = input(prompt).strip()

        try:
            number = int(value)

            if minimum is not None and number < minimum:
                print(f"Please enter a number greater than or equal to {minimum}.")
                continue

            return number

        except ValueError:
            print("Please enter a valid number.")


def handle_add_book():
    """Prompt for book information and add a book."""
    title = input("Enter book title: ").strip()
    isbn = input("Enter ISBN: ").strip()
    year_published = get_integer(
        "Enter year published: ",
        minimum=0
    )
    available_copies = get_integer(
        "Enter available copies: ",
        minimum=0
    )

    try:
        book = add_book(
            title,
            isbn,
            year_published,
            available_copies
        )

        print(f"Book '{book.title}' added successfully!")

    except ValueError as error:
        print(f"Error: {error}")


def handle_add_member():
    """Prompt for member information and add a member."""
    name = input("Enter member name: ").strip()
    email = input("Enter member email: ").strip()

    try:
        member = add_member(name, email)

        print(f"Member '{member.name}' added successfully!")

    except ValueError as error:
        print(f"Error: {error}")


def handle_search_books():
    """Search for books by title."""
    title = input("Enter title to search for: ").strip()

    books = search_books_by_title(title)

    if not books:
        print("No books found.")
        return

    print("\nBooks found:")

    for book in books:
        print(
            f"ID: {book.id} | "
            f"Title: {book.title} | "
            f"ISBN: {book.isbn} | "
            f"Available copies: {book.available_copies}"
        )


def handle_checkout():
    """Display books and check out a selected book."""
    books = list_books()

    if not books:
        print("There are no books in the library.")
        return

    print("\nBooks:")

    for book in books:
        print(
            f"ID: {book.id} | "
            f"Title: {book.title} | "
            f"Available copies: {book.available_copies}"
        )

    book_id = get_integer("Enter book ID: ", minimum=1)
    member_id = get_integer("Enter member ID: ", minimum=1)

    try:
        borrowing = checkout_book(book_id, member_id)

        print("Book checked out successfully!")
        print(f"Borrowing ID: {borrowing.id}")

    except ValueError as error:
        print(f"Error: {error}")


def handle_return():
    """Return a borrowed book."""
    borrowing_id = get_integer(
        "Enter borrowing ID: ",
        minimum=1
    )

    try:
        borrowing = return_book(borrowing_id)

        print("Book returned successfully!")
        print(f"Return date: {borrowing.return_date}")

    except ValueError as error:
        print(f"Error: {error}")


def handle_member_borrowings():
    """Display a member's current borrowings."""
    member_id = get_integer(
        "Enter member ID: ",
        minimum=1
    )

    try:
        borrowings = list_member_borrowings(member_id)

        if not borrowings:
            print("This member has no active borrowings.")
            return

        print("\nCurrent borrowings:")

        for borrowing in borrowings:
            print(
                f"Borrowing ID: {borrowing.id} | "
                f"Book ID: {borrowing.book_id} | "
                f"Checked out: {borrowing.checkout_date}"
            )

    except ValueError as error:
        print(f"Error: {error}")


def handle_overdue():
    """Display all overdue books."""
    try:
        borrowings = list_overdue_books()

        if not borrowings:
            print("No overdue books.")
            return

        print("\nOverdue books:")

        for borrowing in borrowings:
            print(
                f"Borrowing ID: {borrowing.id} | "
                f"Book ID: {borrowing.book_id} | "
                f"Checked out: {borrowing.checkout_date}"
            )

    except ValueError as error:
        print(f"Error: {error}")


def main():
    """Run the Library Management System CLI."""
    init_db()

    while True:
        print("\n📚 Library Management System")
        print("1. Add a book")
        print("2. Add a member")
        print("3. Search books")
        print("4. Check out a book")
        print("5. Return a book")
        print("6. View member's borrowings")
        print("7. View overdue books")
        print("8. Exit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            handle_add_book()

        elif choice == "2":
            handle_add_member()

        elif choice == "3":
            handle_search_books()

        elif choice == "4":
            handle_checkout()

        elif choice == "5":
            handle_return()

        elif choice == "6":
            handle_member_borrowings()

        elif choice == "7":
            handle_overdue()

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()