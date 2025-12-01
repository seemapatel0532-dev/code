"""
Library Automation System - Single-file prototype
Features implemented:
- SQLite database to store books and borrowers
- Classes with inheritance (Person -> User)
- File-based logging of transactions (transactions.log)
- Multithreading simulation of multiple users borrowing/returning concurrently
- Custom exceptions for invalid book IDs and unavailable copies
- Report generation: CSV (borrowed_books.csv) and optional PDF (requires reportlab)

How to run:
- Requires Python 3.8+
- Optional: pip install reportlab (if you want PDF reports)
- Run: python library_management.py

This file will create a SQLite DB file `library.db`, a log file `transactions.log`,
and outputs `borrowed_books.csv` (and `borrowed_books.pdf` if reportlab is installed).

Note: This is a small prototype designed to be easy to expand and to illustrate
all requested concepts: classes/objects, inheritance, file handling, exceptions,
database operations, multithreading.
"""

import sqlite3
import threading
import time
import csv
import os
from datetime import datetime, timedelta

# Optional PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

DB_FILE = 'library.db'
LOG_FILE = 'transactions.log'
CSV_REPORT = 'borrowed_books.csv'
PDF_REPORT = 'borrowed_books.pdf'

# --- Custom Exceptions -----------------------------------------------------
class LibraryError(Exception):
    """Base class for library-related exceptions"""
    pass

class InvalidBookID(LibraryError):
    """Raised when a book id does not exist in the catalog"""
    pass

class NoCopiesAvailable(LibraryError):
    """Raised when a borrow is attempted but no copies remain"""
    pass

# --- Data classes and Inheritance -----------------------------------------
class Person:
    def __init__(self, person_id: int, name: str):
        self.person_id = person_id
        self.name = name

class User(Person):
    """A user that can borrow books; inherits from Person"""
    def __init__(self, person_id: int, name: str, role: str = 'student'):
        super().__init__(person_id, name)
        self.role = role

# --- Database Helper ------------------------------------------------------
class Database:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.lock = threading.Lock()  # protect DB operations across threads
        self._setup()

    def _setup(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    total_copies INTEGER NOT NULL,
                    available_copies INTEGER NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS borrowers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    book_id INTEGER NOT NULL,
                    borrow_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    returned INTEGER DEFAULT 0,
                    return_date TEXT
                )
            ''')

    def add_book(self, title, author, copies=1):
        with self.lock, self.conn:
            cur = self.conn.execute(
                'INSERT INTO books (title, author, total_copies, available_copies) VALUES (?, ?, ?, ?)',
                (title, author, copies, copies)
            )
            return cur.lastrowid

    def get_book(self, book_id):
        cur = self.conn.execute('SELECT id, title, author, total_copies, available_copies FROM books WHERE id=?', (book_id,))
        row = cur.fetchone()
        return row

    def update_copies(self, book_id, delta):
        """Delta may be negative (borrow) or positive (return)."""
        with self.lock, self.conn:
            book = self.get_book(book_id)
            if not book:
                raise InvalidBookID(f"Book with id {book_id} not found")
            available = book[4] + delta
            if available < 0:
                raise NoCopiesAvailable(f"No copies available for book id {book_id}")
            self.conn.execute('UPDATE books SET available_copies=? WHERE id=?', (available, book_id))

    def add_borrow_record(self, user: User, book_id, borrow_date, due_date):
        with self.lock, self.conn:
            self.conn.execute(
                'INSERT INTO borrowers (user_id, user_name, book_id, borrow_date, due_date, returned) VALUES (?, ?, ?, ?, ?, 0)',
                (user.person_id, user.name, book_id, borrow_date.isoformat(), due_date.isoformat())
            )

    def mark_returned(self, user: User, book_id, return_date):
        with self.lock, self.conn:
            # find a matching unreturned record
            cur = self.conn.execute(
                'SELECT id FROM borrowers WHERE user_id=? AND book_id=? AND returned=0 ORDER BY borrow_date LIMIT 1',
                (user.person_id, book_id)
            )
            row = cur.fetchone()
            if not row:
                return False
            borrow_id = row[0]
            self.conn.execute('UPDATE borrowers SET returned=1, return_date=? WHERE id=?', (return_date.isoformat(), borrow_id))
            return True

    def list_borrowed(self):
        cur = self.conn.execute('SELECT id, user_id, user_name, book_id, borrow_date, due_date, returned, return_date FROM borrowers')
        return cur.fetchall()

# --- Logger ---------------------------------------------------------------
class TransactionLogger:
    def __init__(self, file_path=LOG_FILE):
        self.file_path = file_path
        # ensure file exists
        open(self.file_path, 'a').close()
        self.lock = threading.Lock()

    def log(self, message: str):
        timestamp = datetime.now().isoformat()
        line = f"{timestamp} | {message}\n"
        with self.lock:
            with open(self.file_path, 'a') as f:
                f.write(line)

# --- Library Manager ------------------------------------------------------
class LibraryManager:
    def __init__(self, db: Database, logger: TransactionLogger):
        self.db = db
        self.logger = logger

    def borrow_book(self, user: User, book_id: int, days=14):
        try:
            # check book exists
            book = self.db.get_book(book_id)
            if not book:
                raise InvalidBookID(f"Book id {book_id} does not exist")

            # decrement available copies (may raise NoCopiesAvailable)
            self.db.update_copies(book_id, -1)

            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=days)
            self.db.add_borrow_record(user, book_id, borrow_date, due_date)
            msg = f"BORROW: user={user.person_id}-{user.name} borrowed book={book_id} ('{book[1]}') due={due_date.date()}"
            self.logger.log(msg)
            print(msg)
            return True
        except LibraryError as e:
            msg = f"BORROW-FAILED: user={user.person_id}-{user.name} book={book_id} error={e}"
            self.logger.log(msg)
            print(msg)
            return False

    def return_book(self, user: User, book_id: int):
        try:
            # mark returned in borrowers table
            success = self.db.mark_returned(user, book_id, datetime.now())
            if not success:
                msg = f"RETURN-FAILED: user={user.person_id}-{user.name} no outstanding borrow record for book {book_id}"
                self.logger.log(msg)
                print(msg)
                return False

            # increment available copies
            self.db.update_copies(book_id, +1)
            book = self.db.get_book(book_id)
            msg = f"RETURN: user={user.person_id}-{user.name} returned book={book_id} ('{book[1]}')"
            self.logger.log(msg)
            print(msg)
            return True
        except LibraryError as e:
            msg = f"RETURN-FAILED: user={user.person_id}-{user.name} book={book_id} error={e}"
            self.logger.log(msg)
            print(msg)
            return False

# --- Reporting ------------------------------------------------------------
def generate_csv_report(db: Database, csv_path=CSV_REPORT):
    rows = db.list_borrowed()
    header = ['record_id', 'user_id', 'user_name', 'book_id', 'borrow_date', 'due_date', 'returned', 'return_date']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in rows:
            writer.writerow(r)
    print(f"CSV report generated: {csv_path}")

def generate_pdf_report(db: Database, pdf_path=PDF_REPORT):
    if not PDF_AVAILABLE:
        print("PDF generation skipped: reportlab not installed")
        return
    rows = db.list_borrowed()
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, 'Borrowed Books Report')
    y -= 30
    c.setFont('Helvetica', 10)
    header = ['id','user_id','user_name','book_id','borrow_date','due_date','returned','return_date']
    c.drawString(40, y, ' | '.join(header))
    y -= 20
    for r in rows:
        line = ' | '.join(str(x) for x in r)
        c.drawString(40, y, line)
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    print(f"PDF report generated: {pdf_path}")

# --- Multithreaded simulation helpers ------------------------------------

def simulate_user_actions(lmgr: LibraryManager, user: User, actions: list):
    """Actions is a list of tuples: (action_type, book_id, optional_days)
    action_type: 'borrow' or 'return'"""
    for act in actions:
        typ = act[0]
        book_id = act[1]
        if typ == 'borrow':
            days = act[2] if len(act) > 2 else 14
            lmgr.borrow_book(user, book_id, days=days)
        elif typ == 'return':
            lmgr.return_book(user, book_id)
        else:
            print(f"Unknown action {typ}")
        # sleep a bit to simulate user think time
        time.sleep(0.1)

# --- Sample data & main --------------------------------------------------

def seed_data(db: Database):
    # Simple seed of books
    books = [
        ("Introduction to Algorithms", "Cormen", 3),
        ("Clean Code", "Robert C. Martin", 2),
        ("Artificial Intelligence: A Modern Approach", "Russell & Norvig", 1),
        ("Operating System Concepts", "Silberschatz", 2)
    ]
    existing = db.conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    if existing == 0:
        for title, author, copies in books:
            db.add_book(title, author, copies)
        print('Seeded books into database')


def main():
    # Remove old artifacts if you want a fresh run
    # os.remove(DB_FILE) if os.path.exists(DB_FILE) else None

    db = Database()
    logger = TransactionLogger()
    lmgr = LibraryManager(db, logger)

    seed_data(db)

    # Create some users
    users = [
        User(1, 'Alice', 'student'),
        User(2, 'Bob', 'student'),
        User(3, 'Professor X', 'staff')
    ]

    # Define actions for each user to simulate concurrency
    actions = {
        1: [('borrow', 1), ('borrow', 2), ('return', 1)],
        2: [('borrow', 1), ('borrow', 3), ('return', 3)],
        3: [('borrow', 1), ('borrow', 4), ('return', 4)]
    }

    threads = []
    for u in users:
        t = threading.Thread(target=simulate_user_actions, args=(lmgr, u, actions[u.person_id]))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Generate reports
    generate_csv_report(db)
    generate_pdf_report(db)

    print('\nAll done. Check files: {} , {} , {}'.format(DB_FILE, LOG_FILE, CSV_REPORT))
    if PDF_AVAILABLE:
        print('PDF also generated:', PDF_REPORT)

if __name__ == '__main__':
    main()