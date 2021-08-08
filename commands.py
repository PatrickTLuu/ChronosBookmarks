from auth import authenticate
import mysql.connector
import import_html as myHTML
import sys
from datetime import date


sys.tracebacklimit = 0
sql = authenticate()
authenticate.createDatabase(sql)
authenticate.createBookmarkTable(sql)


# Raised if a search returns 0
class NotFoundError(Exception):
    pass


# Raised if a duplicate entry would be created
class AlreadyExistsError(Exception):
    pass


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
    insertVal = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    bookmark = search(name, "-e")
    val = (name, url, notes)

    if bookmark.exists > 0:
        raise AlreadyExistsError("Can't add bookmark. Name already exists")

    else:
        # Adds bookmark to database
        sql.cursor.execute(insertVal, val)
        sql.db.commit()

        return "Bookmark Added."



def editBookmark(name, column, value) -> str:
    """
    Edit bookmarks in the database
    """

    updateVal = {
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
            sql.cursor.execute(updateVal[column], val)
            sql.db.commit()
            return f"Updated {column} of {name}."

        except KeyError:
            raise NotFoundError(f"Unable to find column with name {column}")


def deleteBookmark(name) -> str :
    """
    Delete a bookmark from the database
    """

    # sql script to execute
    deleteVal = "DELETE FROM bookmarks WHERE name = %s"
    bookmark = search(name, "-e")


    # If only one bookmark is returned
    if bookmark.exists == 1:
        confirm = input("Are you sure (Y/N)? ") == "Y"

        if confirm:
            sql.cursor.execute(deleteVal, (name, ))
            sql.db.commit()
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
        "-n": search.bookmark_name_search,
        }

        
        functions[type](self)


    # Finds how many bookmarks match the search query exactly
    def exists_search(self) -> None:
        searchExist = "SELECT id FROM bookmarks WHERE name = %s"
        sql.cursor.execute(searchExist, (self.query, ))
        self.exists = len(sql.cursor.fetchall())


    # Find bookmarks that contain part of a search query
    def bookmark_name_search(self) -> list:
        self.query = f"%{self.query}%"
        searchName = "SELECT * FROM bookmarks WHERE name LIKE %s"

        sql.cursor.execute(searchName, (self.query, ))
        self.bookmarks = sql.cursor.fetchall()
        
        if self.bookmarks == []:
            raise NotFoundError(f"Unable to find bookmark with name like {self.query}.")
