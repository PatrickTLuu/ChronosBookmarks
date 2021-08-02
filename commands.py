import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError
from datetime import date


# Opens the database bookmarks if it exists and if not, creates one
def setup(db, username, password) -> None:
    global mydb 
    global myCursor
    global DATABASE
    global COLUMNS

    DATABASE = db
    COLUMNS = ("name", "url", "notes")
    auth = {
        "host": "localhost",
        "user": username,
        "password": password,
    }

    try:
        # Tries to open the database with bookmarks in it
        mydb = mysql.connector.connect(**auth, database=DATABASE)
        myCursor = mydb.cursor()

    except DatabaseError:
        # If there is no database then create a database
        mydb = mysql.connector.connect(**auth)

        myCursor = mydb.cursor()
        myCursor.execute("CREATE DATABASE %s", (DATABASE, ))
        myCursor.execute("USE %s", (DATABASE, ))
        myCursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
        %s VARCHAR(255), %s VARCHAR(255), %s VARCHAR(255))""", *COLUMNS)


# Authenticate mysql user
def authenticate() -> None:
    # Looks for an auth file in its directory
    file = open("auth.config").read()
    auth = file.split("\n")

    if "database=" in auth[0] and "username=" in auth[1] and "password=" in auth[2]:
        auths = []
        for x in auth:
            auths.append(x.split("=")[1])
        
        setup(*auths)


# Get all bookmarks and prints them
def listBookmarks() -> list:
    sql = "SELECT * FROM bookmarks ORDER BY id"
    bookmarks = []
    myCursor.execute(sql)
    for x in myCursor.fetchall():
        bookmarks.append(x)

    return (True, bookmarks)


def searchBookmark(query, accuracy = None) -> tuple:
    # sql script to execute
    if accuracy == "-s":
        sql = "SELECT * FROM bookmarks WHERE name = %s"
        search = clean.cleanBookmarkValue(query)
    
    else:
        sql = "SELECT * FROM bookmarks WHERE name LIKE %s"
        search = clean.cleanQuery(query)
    
    # Selects bookmarks that match search query
    myCursor.execute(sql, (search, ))     
    fetchBookmarks = myCursor.fetchall()

    # If no bookmarks were found return False with error statement
    if fetchBookmarks == []:
        return (False, "No bookmark matches the search query.")

    # Otherwise return True with list of all bookmarks
    else:
        bookmarks = []
        for x in fetchBookmarks:
            bookmarks.append(x)
        return (True, bookmarks)


# Add a bookmark to the database
def addBookmark(name, url, notes) -> str:
    # sql script to execute
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    val = clean.cleanBookmarkValues((name, url, notes))


    # Adds bookmark to database
    myCursor.execute(sql, val)
    mydb.commit()

    return "Bookmark Added."


# Edit bookmarks already made
def editBookmark(query, column, value) -> str:
    # sql script to execute
    if column == "name":
        sql = "UPDATE bookmarks SET name = %s WHERE name = %s"
    elif column == "url":
        sql = "UPDATE bookmarks SET url = %s WHERE name = %s"
    elif column == "notes":
        sql = "UPDATE bookmarks SET notes = %s WHERE name = %s"
    else:
        return (False, "Column does not exist.")

    val = (clean.cleanBookmarkValues((value, query)))

    # Checks if the one bookmark exists
    search = searchBookmark(query, "-s")
    if not search[0]:
        return (False, "Bookmark does not exist.")

    # Edits bookmark in database
    myCursor.execute(sql, val)
    mydb.commit()
    return "Updated {} of {}.".format(column, query)


# Delete a bookmark from database
def deleteBookmark(name) -> str :
    # sql script to execute
    sql = "DELETE FROM bookmarks WHERE name = %s"
    exists = searchBookmark(name, "-s")


    # If bookmark exists and returned only one bookmark
    if exists[0] and len(exists[1]) == 1:
        print("\n{}".format(exists[1]))
        confirm = str(input("Are you sure (Y/N)? ")) == "Y"

        # Confirms deletion of bookmark
        if confirm:
            name = clean.cleanQuery(name)
            myCursor.execute(sql, (name, ))
            mydb.commit()
            return "Bookmark deleted."
        else:
            return "Canceling Delete."

    # If there was more than one bookmark
    elif exists[0] and len(exists[1]) > 1:
        return "Search query too broad."

    # Otherwise bookmark doesn't exist
    else:
        return "Bookmark does not exist."


#Imports bookmarks from html
def importBookmarks(file) -> str:
    errors = open("log.txt", "a") # Stores bookmarks that failed to be added
    errors.write(date.today().strftime("\n\n%d/%m/%y\n"))


    # Opens the html parser and passes the bookmark file through
    parser = myHTML.BookmarkHTMLParser()
    bookmarks = open(file).read()
    parser.feed(bookmarks)


    # For all the bookmarks from html parse
    for bookmark in myHTML.allBookmarks:
        name = bookmark[1]
        url = bookmark[0][1]
        notes = ""

        # Checks if the bookmark already exists
        findBookmark = searchBookmark(name, "-s")[0]


        # If bookmark doesn't exist
        if not findBookmark:
            try:
                addBookmark(name, url, notes)
            
            # If any of the values are too long, appends to error
            except mysql.connector.errors.DataError:
                errors.write("{}, {}, {}\n".format(name, url, notes))

    # Returns number of bookmarks imported and bookmarks not imported
    return "{} bookmarks imported. Errors stored in log.txt.".format(len(myHTML.allBookmarks)+1)


#Clean bookmarks
class clean:

    # Cleans values to be used in bookmarks
    def cleanBookmarkValue(toClean) -> str:
        illegalChar = ["'", "\"", "%"]

        for char in illegalChar:
            toClean = toClean.replace(char, "")

        return toClean


    def cleanBookmarkValues(toClean) -> tuple:
        cleaned = []
        for value in toClean:
            cleaned.append(clean.cleanBookmarkValue(value))

        return tuple(cleaned)

    # Cleans values to be used in search queries
    def cleanQuery(toClean) -> str:
        illegalChar = ["'", "[", "]", "%"]

        for char in illegalChar:
            toClean = toClean.replace(char, "")

        toClean = toClean.replace(" ", "_")
        toClean = "%{}%".format(toClean)
    
        return toClean