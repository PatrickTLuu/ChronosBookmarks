from re import search
import mysql.connector
import import_html as myHTML
from mysql.connector.errors import DatabaseError


# Opens the database bookmarks if it exists and if not, creates one
def setup():
    global mydb 
    global myCursor

    try:
        mydb = mysql.connector.connect(
            host="localhost", 
            user="USERNAME", 
            password="PASSWORD", 
            database="bookmarks")
        myCursor = mydb.cursor()

    except DatabaseError:
        mydb = mysql.connector.connect(
            host="localhost", 
            user="USERNAME", 
            password="PASSWORD")

        myCursor = mydb.cursor()
        myCursor.execute("CREATE DATABASE bookmarks")
        myCursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255), url VARCHAR(255), notes VARCHAR(255))""")



# Get all bookmarks and prints them
def getBookmarks():
    myCursor.execute("SELECT name FROM bookmarks ORDER BY id")
    bookmarks = myCursor.fetchall()
    for x in bookmarks:
        print(x)


def searchBookmark(mode):
    if mode == "X9itcJqQ43":
        search = input("Search for bookmark: ")
    else:
        search = mode
    
    myCursor.execute("SELECT * FROM bookmarks WHERE name LIKE '{}{}{}'".format("%", search, "%"))
    bookmarks = myCursor.fetchall()
    if bookmarks == []:
        print("Unable to locate bookmark.")
    else:
        for x in bookmarks:
            print(x)


# Add a bookmark to the database
def addBookmark():
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    name = str(input("Enter name of bookmark: "))
    url = str(input("Enter url of bookmark: "))
    notes = str(input("Notes to add to bookmark: "))

    val = cleanBookmark(name, url, notes)
    myCursor.execute(sql, val)
    mydb.commit()
    print("\nBookmark Added.")


def editBookmark(mode):
    sql = "UPDATE bookmarks SET {column} = '{value}' WHERE name LIKE '%{search}%'"
    oldName = input("Enter name of bookmark to update: ")
    searchBookmark(oldName)
    toUpdate = input("What do you want to update? ").lower()

    if toUpdate == "name":
        newEntry = str(input("Enter new name of bookmark: "))
    elif toUpdate == "url":
        newEntry = str(input("Enter new url: "))
    elif toUpdate == "notes":
        newEntry = str(input("Enter new notes: "))
    else:
        return

    myCursor.execute(sql.format(column = toUpdate, value = newEntry, search = oldName))
    mydb.commit()
    print("Updated {column} of {search}.".format(column = toUpdate, search = oldName))


# Delete a bookmark from database
def deleteBookmark():
    sql = "DELETE FROM bookmarks WHERE name = %s"
    name = (input("Enter name of bookmark to delete: "), )
    confirm = str(input("Are you sure (Y/N)? ")) == "Y"

    if confirm:
        myCursor.execute(sql, name)
        mydb.commit()
        print("\nBookmark deleted.")
    else:
        print("\nCanceling Delete.")


#Imports bookmarks from html
def importBookmarks():
    error = []
    parser = myHTML.BookmarkHTMLParser()
    file = "C:/Users/patri.LAPTOP-GHL2QTQE/Documents/Bookmarks.html"
    bookmarks = open(file).read()
    parser.feed(bookmarks)


    sql = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    for bookmark in myHTML.allBookmarks:
        name = bookmark[1]
        url = bookmark[0][1]
        notes = ""

        val = cleanBookmark(name, url, notes)
        search = val[0].replace(" ", "_")

        myCursor.execute("SELECT id FROM bookmarks WHERE name LIKE '%s'" % search)
        findBookmark = myCursor.fetchall()

        if findBookmark == []:
            try:
                myCursor.execute(sql, val)
                mydb.commit()
            
            except mysql.connector.errors.DataError:
                error.append(val)


    print("\n%s bookmarks imported." % str(len(myHTML.allBookmarks)+1))
    print("Unable to import: %s" % error)


#Clean bookmarks
def cleanBookmark(name, url, notes):
    cleanName = name.replace("'", "")
    cleanUrl = url.split("?", 1)[0]
    CleanNotes = notes.replace("'", "")
    return (cleanName, cleanUrl, CleanNotes)



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

            actions[action](args)

        except KeyError:
            pass




