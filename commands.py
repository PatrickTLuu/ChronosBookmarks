import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError


# Opens the database bookmarks if it exists and if not, creates one
def setup():
    global mydb 
    global myCursor

    try:
        # Tries to open the database with bookmarks in it
        mydb = mysql.connector.connect(
            host="localhost", 
            user="USERNAME", 
            password="PASSWORD", 
            database="bookmarks")
        myCursor = mydb.cursor()

    except DatabaseError:
        # If there is no database then create a database
        mydb = mysql.connector.connect(
            host="localhost", 
            user="USERNAME", 
            password="PASSWORD")

        myCursor = mydb.cursor()
        myCursor.execute("CREATE DATABASE bookmarks")
        myCursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255), url VARCHAR(255), notes VARCHAR(255))""")


# Get all bookmarks and prints them
def listBookmarks():
    myCursor.execute("SELECT * FROM bookmarks ORDER BY id")
    bookmarks = myCursor.fetchall()
    toPrint = []
    for x in bookmarks:
        toPrint.append(x)

    return (True, toPrint)


def searchBookmark(query, accuracy = None):
    # sql script to execute
    if accuracy == "-s":
        sql = "SELECT * FROM bookmarks WHERE name = '{}'"
        search = clean("bookmark", [query])[0]
    
    else:
        sql = "SELECT * FROM bookmarks WHERE name LIKE '{}'"
        search = clean("search", query)
    
    # Selects bookmarks that match search query
    myCursor.execute(sql.format(search))
    bookmarks = myCursor.fetchall()

    # If no bookmarks were found return False with error statement
    if bookmarks == []:
        return (False, "No bookmark matches the search query.")

    # Otherwise return True with list of all bookmarks
    else:
        toPrint = []
        for x in bookmarks:
            toPrint.append(x)
        return (True, toPrint)


# Add a bookmark to the database
def addBookmark(name, url, notes):
    # sql script to execute
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES ('{}','{}','{}')"
    val = clean("bookmark", (name, url, notes))


    # Adds bookmark to database
    myCursor.execute(sql.format(*val))
    mydb.commit()
    return (True, "Bookmark Added.")


# Edit bookmarks already made
def editBookmark(query, column, value):
    # sql script to execute
    sql = "UPDATE bookmarks SET {column} = '{value}' WHERE name LIKE '{search}'"
    query = clean("bookmark", [query])[0]
    value = clean("bookmark", [value])[0]

    # Checks if the one bookmark exists
    search = searchBookmark(query, "-s")
    if not search[0]:
        return (False, "Bookmark does not exist.")

    elif not (len(search[1]) == 1):
        return (False, "Name to search for is too broad.")


    columns = ["name", "url", "notes"]
    if column not in columns:
        return (False, "Column does not exist.")

    # Edits bookmark in database
    myCursor.execute(sql.format(column = column, value = value, search = query))
    mydb.commit()
    return (True, "Updated {column} of {search}.".format(column = column, search = query))


# Delete a bookmark from database
def deleteBookmark(name):
    # sql script to execute
    sql = "DELETE FROM bookmarks WHERE name = '{}'"
    exists = searchBookmark(name, "-s")


    # If bookmark exists and returned only one bookmark
    if exists[0] and len(exists[1]) == 1:
        print("\n{}".format(exists[1]))
        confirm = str(input("Are you sure (Y/N)? ")) == "Y"

        # Confirms deletion of bookmark
        if confirm:
            name = clean("bookmark", name)[0]
            myCursor.execute(sql.format(name))
            mydb.commit()
            return (True, "Bookmark deleted.")
        else:
            return (False, "Canceling Delete.")

    # If there was more than one bookmark
    elif exists[0] and len(exists[1]) > 1:
        return (False, "Search query too broad.")

    # Otherwise bookmark doesn't exist
    else:
        return (False, "Bookmark does not exist.")



#Imports bookmarks from html
def importBookmarks(file):
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
    return (True, "{} bookmarks imported.\nUnable to import: {}".format(len(myHTML.allBookmarks)+1, error))


#Clean bookmarks
def clean(mode, toClean):

    # If cleaning a bookmark
    if mode == "bookmark":
        cleaned = []
        for x in toClean:
            x = x.replace("?", "")
            x = x.replace("'", "")
            cleaned.append(x)
        cleaned = tuple(cleaned)

    # If cleaning a search query
    elif mode == "search":
        toClean = str(toClean).replace("'", "")
        toClean = (toClean.replace("[", "")).replace("]", "")
        toClean = toClean.replace(" ", "_")
        toClean = "%{}%".format(toClean)
        cleaned = toClean
    
    return cleaned