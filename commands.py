import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError
from datetime import date


# Raised if a search returns 0
class NotFoundError(Exception):
    pass


# Raised if a duplicate entry would be created
class AlreadyExistsError(Exception):
    pass


def setup(db, username, password) -> None:
    """
    Opens the database chronosbookmarks and 
    connects to the bookmarks table. Creates any
    missing requirements.
    """

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


def authenticate() -> None:
    """
    Opens a auth.config file in the current directory
    anc checks if it has all the required values
    """

    file = open("auth.config").read()
    auth = file.split("\n")

    if "database=" in auth[0] and "username=" in auth[1] and "password=" in auth[2]:
        auths = []
        for x in auth:
            auths.append(x.split("=")[1])
        
        setup(*auths)



def listBookmarks() -> None:
    """
    Passes a wild card to the search class
    to find all bookmarks
    """

    query = "%"
    list = search(query, "-n")
    return list



def addBookmark(name, url, notes) -> str:
    """
    Add a bookmark to the database
    """

    # sql script to execute
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    bookmark = search(name, "-e")
    val = (name, url, notes)

    if bookmark.exists > 0:
        raise AlreadyExistsError("Can't add bookmark. Name already exists")

    else:
        # Adds bookmark to database
        myCursor.execute(sql, val)
        mydb.commit()

        return "Bookmark Added."



def editBookmark(name, column, value) -> str:
    """
    Edit bookmarks in the database
    """

    sql = {
        "name": "UPDATE bookmarks SET name = %s WHERE name = %s",
        "url": "UPDATE bookmarks SET url = %s WHERE name = %s",
        "notes": "UPDATE bookmarks SET notes = %s WHERE name = %s"
    }
    val = (value, name)
    
    # Checks if the one bookmark exists
    bookmark = search(name, "-e")

    if bookmark.exists < 1:
        raise NotFoundError(f"Unable to find bookmark with name {name}.")

    elif bookmark.exists > 1:
        raise NotFoundError(f"Too many results recieved.")

    else:

        # Edits bookmark in database
        try:
            myCursor.execute(sql[column], val)
            mydb.commit()
            return f"Updated {column} of {name}."

        except KeyError:
            raise NotFoundError(f"Unable to find column with name {column}")


def deleteBookmark(name) -> str :
    """
    Delete a bookmark from the database
    """

    # sql script to execute
    sql = "DELETE FROM bookmarks WHERE name = %s"
    bookmark = search(name, "-e")


    # If only one bookmark is returned
    if bookmark.exists == 1:
        confirm = input("Are you sure (Y/N)? ") == "Y"

        if confirm:
            myCursor.execute(sql, (name, ))
            mydb.commit()
            return "Bookmark deleted."
        else:
            return "Canceling Delete."

    # Raise error if more than 1 result
    elif bookmark.exists > 1:
        raise NotFoundError(f"Too many results recieved.")

    # Raise error if not able to find a result
    else:
        raise NotFoundError(f"Unable to find bookmark with name {name}.")


def importBookmarks(file) -> str:
    """
    Import bookmarks from an html file
    """

    errors = open("log.txt", "a") # Stores bookmarks that failed to be added
    errors.write(date.today().strftime("\n\n%d/%m/%y\n"))


    # Opens the html parser and passes the bookmark file through
    parser = myHTML.BookmarkHTMLParser()
    bookmarks = open(file).read()
    parser.feed(bookmarks)


    # For all the bookmarks from html parse
    importNumber = 0
    errorNumber = 0
    for bookmark in myHTML.allBookmarks:
        name, url = bookmark
        notes = ""

        # Checks if the bookmark already exists
        bookmark = search(name, "-e")


        # If bookmark doesn't exist
        if bookmark.exists == 0:
            try:
                addBookmark(name, url, notes)
                importNumber += 1
            
            # If any of the values are too long, appends to error
            except mysql.connector.errors.DatabaseError:
                errors.write(f"Bookmark too long: {name}, {url}, {notes}\n")
                errorNumber += 1

        else:
            errors.write(f"Bookmark name already exists: {name}, {url}, {notes}\n")
            errorNumber += 1


    # Returns number of bookmarks imported and bookmarks not imported
    return f"{importNumber} bookmarks imported. {errorNumber} errors stored in log.txt."


class search:
    """
    Search class to allow for expansion
    on different search queries
    """

    def __init__(self, query, type="-n") -> None:
        self.query = query
        functions = {
        "-e": search.exists_search,
        "-n": search.bookmark_name_search
        }

        
        functions[type](self)


    # Finds how many bookmarks match the search query exactly
    def exists_search(self) -> None:
        sql = "SELECT id FROM bookmarks WHERE name = %s"
        myCursor.execute(sql, (self.query, ))
        self.exists = len(myCursor.fetchall())


    # Find bookmarks that contain part of a search query
    def bookmark_name_search(self) -> list:
        self.query = f"%{self.query}%"
        sql = "SELECT * FROM bookmarks WHERE name LIKE %s"

        myCursor.execute(sql, (self.query, ))
        self.bookmarks = myCursor.fetchall()
        
        if self.bookmarks == []:
            raise NotFoundError(f"Unable to find bookmark with name like {self.query}.")
