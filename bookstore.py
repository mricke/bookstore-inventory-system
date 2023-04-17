import sqlite3
from tabulate import tabulate


# 06/02/2023:
# Removed main() function to ensure all functions are defined in global scope and at the top.
# Entering or updating book details now uses multiple input strings instead of a single input string.

def enter_book():
    """Prompts user for list of book id, Title, Author, and Quantity.
    If valid, insert record into books otherwise do nothing.
    """

    errors = [""]
    book = []
    book.append(input("\nEnter book ID: "))
    book.append(input("Enter Title: "))
    book.append(input("Enter Author: "))
    book.append(input("Enter quantity: "))

    # Most of this is an attempt to validate the user's input
    # and terminate the function early if invalid
    for i in range(len(book)):
        book[i] = book[i].strip().lstrip()
    try:
        book[0] = int(book[0])
        book[3] = int(book[3])
    except ValueError:
        pass
    if type(book[0]) is str:
        errors.append("Error: Number not entered for ID.")
    elif book[0] < 0:
        errors.append("Error: negative id entered for book.")
    if type(book[3]) is str:
        errors.append("Error: Number not entered for quantity.")
    elif book[3] < 0:
        errors.append("Error: negative quantity entered for book.")
    if len(book[1]) == 0:
        errors.append("Error: No title entered.")
    if len(book[2]) == 0:
        errors.append("Error: No Author entered.")
    if len(errors) > 1:
        for error in errors:
            print(error)
        return None
            
    # Here, we check if book[0] exists as an id in ebookstore.db
    # If it doesn't exist, the new book can be inserted into the 'books' table
    cursor.execute('''SELECT id FROM books WHERE id=?''', (book[0],))
    if cursor.fetchone() is not None:
        print(f"\nBook with ID of {book[0]} already exists. No book added to database.")
    else:
        cursor.execute('''INSERT INTO books(id, Title, Author, Qty)
        VALUES(?,?,?,?)''', book)
        db.commit()

def update_book():
    """Prompts user for a book id. If id exists, prompt user for list
    of Title, Author, and quantity. Any values the user wishes not to change can be left blank.
    """

    # User input 'book_id' is checked against 'id' in 'books' table.
    # If there is no match, terminate 'update_books()'
    book_id = input("\nEnter book id: ")
    try:
        book_id = int(book_id)
        cursor.execute('''SELECT * FROM books WHERE id=?''', (book_id,))
        book_row = cursor.fetchone()
        if book_row is None:
            print(f"\nError: Book with ID of {book_id} doesn't exist. Doing nothing.")
            return None
    except TypeError:
        print("\nError: Invalid book ID.")
        return None

    # Requests user input for and checks validity of Title, Author and Qty.
    errors = [""]
    book_row = list(book_row)[1:]
    book_mod = []
    print("\nHint: Leave blank anything you don't want to change.\n")
    book_mod.append(input("Enter Title: "))
    book_mod.append(input("Enter Author: "))
    book_mod.append(input("Enter quantity: "))
    for i in range(len(book_mod)):
        book_mod[i] = book_mod[i].strip().lstrip()
    try:
        book_mod[2] = int(book_mod[2])
        if book_mod[2] < 0:
            print("\nError: Cannot use negative number for quantity.")
            return None
    except ValueError:
        if len(book_mod[2]) > 1:
            print("\nError: Quantity must be an integer.")
            return None

    # Determines if any changes should be made to row and if so, which columns
    # Where user has entered empty column data, no changes will be made to that column
    mod_row = False
    for i in range(len(book_mod)):
        if type(book_mod[i]) is str and len(book_mod[i]) > 0:
            book_row[i] = book_mod[i]
            mod_row = True
        elif type(book_mod[i]) is int:
            book_row[i] = book_mod[i]
            mod_row = True
    if mod_row:
        book_row.append(book_id)
        book_row = tuple(book_row)
        cursor.execute('''UPDATE books SET Title = ?, Author = ?, Qty = ? WHERE id = ? ''', book_row)
        db.commit()
    else:
        print("\nDidn't enter anything. Doing nothing.")

def delete_book():
    """User is prompted for a book id. If book id exists, delete record of book id from 'books' table,
    otherwise do nothing.
    """

    book_id = input("\nEnter book id: ")
    try:
        book_id = int(book_id)
        cursor.execute('''SELECT id FROM books WHERE id=?''', (book_id,))
        if cursor.fetchone() is None:
            print(f"\nError: Book with ID of {book_id} doesn't exist. Doing nothing.")
        else:
            cursor.execute('''DELETE FROM books WHERE id = ?''', (book_id,))
            db.commit()
    except TypeError:
        print("\nError: Invalid book ID.")

def search_book():
    """Prompts user to search by: book ID, book title or book Author.
    Displays table of results if search returns anything.
    """

    while True:
        search_menu = input('''
1. Search by book ID
2. Search by book Title
3. Search by book Author
0. Return to Main Menu
                       ''')
        try:
            search_menu = int(search_menu)

            # Search by ID
            if search_menu == 1:
                search_term = input("\nBook ID: ")
                try:
                    search_term = int(search_term)
                    if search_term < 0:
                        print("\nError: Entered a negative book ID.")
                    else:
                        sql = f"SELECT * FROM books WHERE id = {search_term}"
                        cursor.execute(sql)
                        search_result = cursor.fetchall()
                        if len(search_result) == 0:
                            print("\nNo book found.")
                        else:
                            search_result = [("id", "Title", "Author", "Qty")] + search_result
                            print("")
                            print(tabulate(search_result,headers='firstrow',tablefmt='fancy_grid'))
                except ValueError:
                    print("\nError: Enter an integer for a book ID.")                    

            # Search by Title
            # Uses LIKE keyword to case-insensitive search for search_term anywhere in Title
            elif search_menu == 2:
                search_term = input("\nTitle: ")
                sql = f"SELECT * FROM books \
WHERE Title LIKE '%{search_term}%'"
                cursor.execute(sql)
                search_result = cursor.fetchall()
                if len(search_result) == 0:
                    print("\nNo book found.")
                else:
                    search_result = [("id", "Title", "Author", "Qty")] + search_result
                    print("")
                    print(tabulate(search_result,headers='firstrow',tablefmt='fancy_grid'))

            # Search by Author
            # Works similarly to search by Title.
            elif search_menu == 3:
                search_term = input("\nAuthor: ")
                sql = f"SELECT * FROM books \
WHERE Author LIKE '%{search_term}%'"
                cursor.execute(sql)
                search_result = cursor.fetchall()
                if len(search_result) == 0:
                    print("\nNo book found.")
                else:
                    search_result = [("id", "Title", "Author", "Qty")] + search_result
                    print("")
                    print(tabulate(search_result,headers='firstrow',tablefmt='fancy_grid'))
            elif search_menu == 0:
                break
            else:
                print("\nError: Invalid menu option. Try again.")
        except ValueError:
            print("\nError: Invalid menu option. Try again.")

def init_db():
    """Create table 'books' if it doesn't exist, then populate 'books' if empty."""

    cursor.execute('''CREATE TABLE IF NOT EXISTS
    books(id INTEGER PRIMARY KEY, Title TEXT, Author TEXT, Qty INTEGER)''')
        
    cursor.execute('''SELECT COUNT(1) WHERE EXISTS (SELECT * FROM books)''')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO books
        VALUES
        (3001, 'A Tale of Two Cities', 'Charles Dickens', 30),
        (3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
        (3003, 'The Lion, the Witch and the Wardrobe', 'C.S. Lewis', 25),
        (3004, 'The Lord of the Rings', 'J.R.R. Tolkien', 37),
        (3005, 'Alice in Wonderland', 'Lewis Carroll', 12)''')
        db.commit()

db = sqlite3.connect('ebookstore.db')
cursor = db.cursor()
init_db()
print("ebookstore")

# The Main Menu
while True:
    userinput = input('''
1. Enter book
2. Update book
3. Delete book
4. Search books
0. Exit
              ''')
    try:
        userinput = int(userinput)
        # Enter book
        if userinput == 1:
            enter_book()
        # Update book
        elif userinput == 2:
            update_book()
        # Delete book
        elif userinput == 3:
            delete_book()
        # Search books
        elif userinput == 4:
            search_book()
        elif userinput == 0:
            db.close()
            quit()
    except ValueError:
        print("\nInvalid option. Try again.")


