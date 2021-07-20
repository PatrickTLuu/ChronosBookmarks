import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError

"""
Notes:
X9itcJqQ43 = Random string stating that a function was called manually
"""

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
def getBookmarks(mode):
    myCursor.execute("SELECT * FROM bookmarks ORDER BY id")
    bookmarks = myCursor.fetchall()
    toPrint = []
    for x in bookmarks:
        toPrint.append("{}\n".format(x))

    return toPrint

def searchBookmark(mode):
    # sql script to execute
    sql = "SELECT * FROM bookmarks WHERE name LIKE '{}{}{}'"

    # Gets input from user if called in human mode
    if mode == "X9itcJqQ43":
        search = clean("search", input("Search for bookmark: "))

    # Otherwise, the search query was stored in the mode
    else:
        search = mode
    
    # Selects bookmarks that match search query
    myCursor.execute(sql.format("%", search, "%"))
    bookmarks = myCursor.fetchall()

    # If no bookmarks were found return False with error statement
    if bookmarks == []:
        return (False, "No bookmark matches the search query.")

    # Otherwise return True with list of all bookmarks
    else:
        toPrint = []
        for x in bookmarks:
            toPrint.append("{}\n".format(toPrint))
        return (True, toPrint)


# Add a bookmark to the database
def addBookmark(mode):
    # sql script to execute
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES ({},{},{})"

    # Gets input from user if called in human mode
    if mode == "X9itcJqQ43":
        name = str(input("Enter name of bookmark: "))
        url = str(input("Enter url of bookmark: "))
        notes = str(input("Notes to add to bookmark: "))
        val = clean("Bookmark", name, url, notes)

    # Otherwise the values were stored in the mode
    else:
        val = mode

    # Adds bookmark to database
    myCursor.execute(sql.format(val))
    mydb.commit()
    return (True, "Bookmark Added.")


# Edit bookmarks already made
def editBookmark(mode):
    # sql script to execute
    sql = "UPDATE bookmarks SET {column} = '{value}' WHERE name LIKE '%{search}%'"

    # Checks if the bookmark actually exists
    isValid = False
    while not isValid:
        oldName = input("Enter name of bookmark to update: ")
        isValid = searchBookmark(oldName) 


    # Checks if option is valid
    isValid = False
    while not isValid:
        toUpdate = input("What do you want to update? ").lower()

        if toUpdate == "name":
            newEntry = str(input("Enter new name of bookmark: "))
        elif toUpdate == "url":
            newEntry = str(input("Enter new url: "))
        elif toUpdate == "notes":
            newEntry = str(input("Enter new notes: "))
        else:
            pass

    # Edits bookmark in database
    myCursor.execute(sql.format(column = toUpdate, value = newEntry, search = oldName))
    mydb.commit()
    return (True, "Updated {column} of {search}.".format(column = toUpdate, search = oldName))


# Delete a bookmark from database
def deleteBookmark(mode):
    # sql script to execute
    sql = "DELETE FROM bookmarks WHERE name = %s"

    # Gets input from user if called in human mode
    if mode == "X9itcJqQ43":
        name = (input("Enter name of bookmark to delete: "), )
        confirm = str(input("Are you sure (Y/N)? ")) == "Y"

        # Confirms deletion of bookmark
        if confirm:
            myCursor.execute(sql, name)
            mydb.commit()
            return (True, "Bookmark deleted.")
        else:
            return (False, "Canceling Delete.")

    # Otherwise the value was stored in mode
    else:
        name = mode
        myCursor.execute(sql, name)
        mydb.commit()




#Imports bookmarks from html
def importBookmarks(mode):
    error = [] # Stores bookmarks that failed to be added

    # Opens the html parser and passes the bookmark file through
    parser = myHTML.BookmarkHTMLParser()
    file = input("Enter path of bookmark: ")
    bookmarks = open(file).read()
    parser.feed(bookmarks)


    # For all the bookmarks from html parse
    for bookmark in myHTML.allBookmarks:
        name = bookmark[1]
        url = bookmark[0][1]
        notes = ""

        val = clean("bookmark", (name, url, notes))
        search = clean("search", name)

        # Checks if the bookmark already exists
        findBookmark = search(name)


        # If bookmark doesn't exist
        if not findBookmark:
            try:
                addBookmark(val)
            
            # If any of the values are too long, appends to error
            except mysql.connector.errors.DataError:
                error.append(val)

    # Returns number of bookmarks imported and bookmarks not imported
    return ("{} bookmarks imported.\nUnable to import: {}".format(len(myHTML.allBookmarks)+1, error))


#Clean bookmarks
def clean(mode, toClean):

    # If cleaning a bookmark
    if mode == "bookmark":
        cleaned = []
        for x in toClean:
            x = x.replace("?", "")
            x = x.replace("'", "")
            cleaned.append(x)

    # If cleaning a search query
    elif mode == "search":
        toClean = toClean.replace(" ", "_")
        toClean = "%{}%".format(toClean)
        cleaned = toClean
    
    return cleaned



if __name__ == '__main__':
    active = True
    actions = {
        "list bookmarks": getBookmarks,
        "search bookmark": searchBookmark,
        "add bookmark": addBookmark,
        "edit bookmark": editBookmark,
        "delete bookmark": deleteBookmark,
        "import bookmarks": importBookmarks,
        "exit": exit
    }
    setup()

    while active:
        try:
            print("\n\nActions avalible: List Bookmarks, Search Bookmark, Add Bookmark, Edit Bookmark, Delete Bookmark, Import Bookmarks, Exit")
            action = str(input(">>> ")).lower()
            args = "X9itcJqQ43"

            toPrint = actions[action](args)
            print("\n" + toPrint)
        except KeyError:
            pass




