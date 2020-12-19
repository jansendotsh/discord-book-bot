import os, sqlite3
from goodreads import client as gcclient
from config import GOODREADS_KEY,GOODREADS_SECRET

# sqlite3 data source
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "db/bookbot.db")

# Goodreads API
gc = gcclient.GoodreadsClient(GOODREADS_KEY, GOODREADS_SECRET)

# Checking that the database is okay
if os.path.exists(db_path):
    overwrite = ""
    while(overwrite != "Y" and overwrite != "N"):
        overwrite = input("You currently have a database. Do you want to overwrite? (Y/N) ").upper()
    
    if overwrite == "Y":
        print("Backing up the current database...")
        backup_db = os.path.join(base_dir, "db/bookbot.db.backup")
        os.rename(db_path, backup_db)
    elif overwrite == "N":
        print("Bailing out!")
        quit()
    else:
        print("No clue what happened here... Try again?")
        quit()

## Create database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE "current" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"author"	TEXT NOT NULL,
	"goodreads_id"	INTEGER NOT NULL,
    "thumbnail" TEXT NOT NULL,
	"pages"	INTEGER,
	"ebook_link"	TEXT,
	"abook_link"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)''')
cursor.execute('''CREATE TABLE "next" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"author"	TEXT NOT NULL,
	"goodreads_id"	INTEGER NOT NULL,
    "thumbnail" TEXT NOT NULL,
	"pages"	INTEGER,
	"ebook_link"	TEXT,
	"abook_link"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)''')
cursor.execute('''CREATE TABLE "pool" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"author"	TEXT NOT NULL,
	"goodreads_id"	INTEGER NOT NULL,
    "thumbnail" TEXT NOT NULL,
	"pages"	INTEGER,
	"ebook_link"	TEXT,
	"abook_link"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)''')
cursor.execute('''CREATE TABLE "past" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"author"	TEXT NOT NULL,
	"goodreads_id"	INTEGER NOT NULL,
    "thumbnail" TEXT NOT NULL,
	"pages"	INTEGER,
	"ebook_link"	TEXT,
	"abook_link"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)''')
cursor.execute('''CREATE TABLE "progress" (
	"user"	TEXT NOT NULL,
	"progress"	INTEGER NOT NULL
)''')
connection.commit()
print("\nCreated the database...")

## Add a current book
print("This will be the book that you're reading now, populating the `current` database")
id = input("Goodreads ID for the current book: ")
try:
    bookShow = gc.book(id)
    
    title = bookShow._book_dict['title']
    grid = bookShow._book_dict['id']
    pageCount = bookShow._book_dict['num_pages']
    author = ""

    if isinstance(bookShow._book_dict['authors']['author'], list):
        for i in bookShow._book_dict['authors']['author']:
            if i['role'] == None:
                author += "{}, ".format(i['name'])
            if i['role'] != None:
                author += "{} ({}), ".format(i['name'], i['role'])

        author = author[:-2]

    elif isinstance(bookShow._book_dict['authors']['author'], dict):
        author = bookShow._book_dict['authors']['author']['name']
except:
    print("Goodreads API was unresponsive, check your API keys and connection")

query = ("INSERT INTO current(title, author, goodreads_id, thumbnail, pages) VALUES (?, ?, ?, ?, ?)")
bookAdd = (bookShow._book_dict['title'], author, bookShow._book_dict['id'], bookShow._book_dict['small_image_url'], bookShow._book_dict['num_pages'])
cursor.execute(query, bookAdd)
connection.commit()

print("Added!")

## Add next book
print("This is the second book to be read which will populate the `next` database.")
id = input("Goodreads ID for the next book: ")
try:
    bookShow = gc.book(id)
    
    title = bookShow._book_dict['title']
    grid = bookShow._book_dict['id']
    pageCount = bookShow._book_dict['num_pages']
    author = ""

    if isinstance(bookShow._book_dict['authors']['author'], list):
        for i in bookShow._book_dict['authors']['author']:
            if i['role'] == None:
                author += "{}, ".format(i['name'])
            if i['role'] != None:
                author += "{} ({}), ".format(i['name'], i['role'])

        author = author[:-2]

    elif isinstance(bookShow._book_dict['authors']['author'], dict):
        author = bookShow._book_dict['authors']['author']['name']
except:
    print("Goodreads API was unresponsive, check your API keys and connection")

query = ("INSERT INTO next(title, author, goodreads_id, thumbnail, pages) VALUES (?, ?, ?, ?, ?)")
bookAdd = (bookShow._book_dict['title'], author, bookShow._book_dict['id'], bookShow._book_dict['small_image_url'], bookShow._book_dict['num_pages'])
cursor.execute(query, bookAdd)
connection.commit()

print("Added!")

print("You now have a database and are ready to launch the app. You can add further books via Discord `b!add`")