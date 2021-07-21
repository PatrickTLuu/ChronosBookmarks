from tkinter.constants import X
import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError

"""
Notes:
X9itcJqQ43 = Random string stating that a function was called manually, used to avoid search query conflict
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
def listBookmarks():
    myCursor.execute("SELECT * FROM bookmarks ORDER BY id")
    bookmarks = myCursor.fetchall()
    toPrint = []
    for x in bookmarks:
        toPrint.append(x)

    return (True, toPrint)

def searchBookmark(mode = "X9itcJqQ43", accuracy = None):
    # sql script to execute
    if accuracy == "specific":
        sql = "SELECT * FROM bookmarks WHERE name = '{}'"
        search = clean("search", mode)
    
    else:
        sql = "SELECT * FROM bookmarks WHERE name LIKE '{}'"

        # Gets input from user if called in human mode
        if mode == "X9itcJqQ43":
            search = clean("search", input("\nSearch for bookmark: "))

        # Otherwise, the search query was stored in the mode
        else:
            search = clean("search", mode)
    
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
def addBookmark(mode = "X9itcJqQ43"):
    # sql script to execute
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES ('{}','{}','{}')"

    # Gets input from user if called in human mode
    if mode == "X9itcJqQ43":
        name = str(input("\nEnter name of bookmark: "))
        url = str(input("Enter url of bookmark: "))
        notes = str(input("Notes to add to bookmark: "))
        val = clean("bookmark", (name, url, notes))

    # Otherwise the values were stored in the mode
    else:
        val = clean(mode)

    # Adds bookmark to database
    myCursor.execute(sql.format(*val))
    mydb.commit()
    return (True, "Bookmark Added.")


# Edit bookmarks already made
def editBookmark():
    # sql script to execute
    sql = "UPDATE bookmarks SET {column} = '{value}' WHERE name LIKE '{search}'"

    # Checks if the one bookmark  exists
    isValid = False
    while not isValid:
        oldName = input("Enter name of bookmark to update: ")
        search = searchBookmark(oldName, "specific")
        isValid = search[0] and len(search[1]) == 1


    # Checks if option is valid
    isValid = False
    while not isValid:
        toUpdate = input("What do you want to update? ").lower()

        if toUpdate == "name":
            newEntry = str(input("Enter new name of bookmark: "))
            isValid = True
        elif toUpdate == "url":
            newEntry = str(input("Enter new url: "))
            isValid = True
        elif toUpdate == "notes":
            newEntry = str(input("Enter new notes: "))
            isValid = True
        else:
            pass

    # Edits bookmark in database
    myCursor.execute(sql.format(column = toUpdate, value = newEntry, search = oldName))
    mydb.commit()
    return (True, "Updated {column} of {search}.".format(column = toUpdate, search = oldName))


# Delete a bookmark from database
def deleteBookmark(mode = "X9itcJqQ43"):
    # sql script to execute
    sql = "DELETE FROM bookmarks WHERE name = '{}'"

    # Gets input from user if called in human mode
    if mode == "X9itcJqQ43":
        name = input("Enter name of bookmark to delete: ")
        exists = searchBookmark(name, "specific")

        # If bookmark exists and returned only one bookmark
        if exists[0] and len(exists[1]) == 1:
            print(exists[1])
            confirm = str(input("Are you sure (Y/N)? ")) == "Y"

            # Confirms deletion of bookmark
            if confirm:
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

    # Otherwise the value was stored in mode
    else:
        name = clean("search", mode)
        myCursor.execute(sql, name)
        mydb.commit()




#Imports bookmarks from html
def importBookmarks():
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

        val = (name, url, notes)

        # Checks if the bookmark already exists
        findBookmark = searchBookmark(name, "specific")


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
        toClean = toClean.replace("'", "")
        toClean = toClean.replace(" ", "_")
        toClean = "%{}%".format(toClean)
        cleaned = toClean
    
    return cleaned



if __name__ == '__main__':
    active = True
    actions = {
        "list bookmarks": listBookmarks,
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

            toPrint = actions[action]()

            # If the function returned a tuple or list to be printed, print each value
            if isinstance(toPrint[1], (list, tuple)):
                for x in toPrint[1]:
                    print("\n{}".format(x))

            # Otherwise just print returned value
            else:
                print("\n{}".format(toPrint[1]))

        except KeyError:
            pass




