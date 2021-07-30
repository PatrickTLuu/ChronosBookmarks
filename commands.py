import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError


# Opens the database bookmarks if it exists and if not, creates one
def setup(db, username, password) -> None:
    global mydb 
    global myCursor
    global DATABASE
    global COLUMNS

    DATABASE = db
    COLUMNS = ["name", "url", "notes"]
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
        myCursor.execute("CREATE DATABASE {}".format(DATABASE))
        myCursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
        {} VARCHAR(255), {} VARCHAR(255), {} VARCHAR(255))""".format(*COLUMNS))


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
    sql = "SELECT * FROM {} ORDER BY id".format(DATABASE)
    bookmarks = []
    myCursor.execute(sql)
    for x in myCursor.fetchall():
        bookmarks.append(x)

    return (True, bookmarks)


def searchBookmark(query, accuracy = None) -> tuple:
    # sql script to execute
    if accuracy == "-s":
        sql = "SELECT * FROM {} WHERE name = '{}'"
        search = clean.cleanQuery(query)
    
    else:
        sql = "SELECT * FROM {} WHERE name LIKE '%{}%'"
        search = clean.cleanQuery(query)
    
    # Selects bookmarks that match search query
    myCursor.execute(sql.format(DATABASE, search))
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
    sql = "INSERT INTO {} (name, url, notes) VALUES ('{}','{}','{}')"
    val = clean("bookmark", (name, url, notes))


    # Adds bookmark to database
    myCursor.execute(sql.format(DATABASE, *val))
    mydb.commit()

    return "Bookmark Added."


# Edit bookmarks already made
def editBookmark(query, column, value) -> str:
    # sql script to execute
    sql = "UPDATE {} SET {column} = '{value}' WHERE name LIKE '{search}'"
    val = [clean.cleanBookmark([value]), clean.cleanQuery(query)]

    # Checks if the one bookmark exists
    search = searchBookmark(val[1], "-s")
    if not search[0]:
        return (False, "Bookmark does not exist.")

    if column not in COLUMNS:
        return (False, "Column does not exist.")

    # Edits bookmark in database
    myCursor.execute(sql.format(DATABASE, column = column, value = value, search = query))
    mydb.commit()
    return "Updated {column} of {search}.".format(column = column, search = query)


# Delete a bookmark from database
def deleteBookmark(name) -> str :
    # sql script to execute
    sql = "DELETE FROM {} WHERE name = '{}'"
    exists = searchBookmark(name, "-s")


    # If bookmark exists and returned only one bookmark
    if exists[0] and len(exists[1]) == 1:
        print("\n{}".format(exists[1]))
        confirm = str(input("Are you sure (Y/N)? ")) == "Y"

        # Confirms deletion of bookmark
        if confirm:
            name = clean.cleanQuery(name)
            myCursor.execute(sql.format(DATABASE, name))
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
    error = [] # Stores bookmarks that failed to be added

    # Opens the html parser and passes the bookmark file through
    parser = myHTML.BookmarkHTMLParser()
    bookmarks = open(file).read()
    parser.feed(bookmarks)


    # For all the bookmarks from html parse
    for bookmark in myHTML.allBookmarks:
        name = bookmark[1]
        url = bookmark[0][1]
        notes = ""

        val = (name, url, notes)

        # Checks if the bookmark already exists
        findBookmark = searchBookmark(name, "-s")


        # If bookmark doesn't exist
        if not findBookmark:
            try:
                addBookmark(val)
            
            # If any of the values are too long, appends to error
            except mysql.connector.errors.DataError:
                error.append(val)

    # Returns number of bookmarks imported and bookmarks not imported
    return "{} bookmarks imported.\nUnable to import: {}".format(len(myHTML.allBookmarks)+1, error)


#Clean bookmarks
class clean:

    # Cleans values to be used in bookmarks
    def cleanBookmark(toClean) -> (tuple or str):
        illegalChar = ["'", "\"", "%"]
        cleaned = []

        for val in toClean:
            for char in illegalChar:
                val = val.replace(char, "")

            cleaned.append(val)

        if len(cleaned) > 1:
            return tuple(cleaned)
        
        else:
            return str(cleaned)


    # Cleans values to be used in search queries
    def cleanQuery(toClean) -> str:
        illegalChar = ["'", "[", "]", "%"]

        for char in illegalChar:
            toClean = toClean.replace(char, "")

        toClean = toClean.replace(" ", "_")
    
        return toClean