import mysql.connector
from mysql.connector.errors import DatabaseError


# Opens the database bookmarks if it exists and if not, creates one
def setup():
    global mydb 
    global myCursor

    try:
        mydb = mysql.connector.connect(
            host="localhost", 
            user="INSERT USER", 
            password="INSERT PASSWORD", 
            database="bookmarks")
        myCursor = mydb.cursor()

    except DatabaseError:
        mydb = mysql.connector.connect(
            host="localhost", 
            user="INSERT USER", 
            password="INSERT PASSWORD")

        myCursor = mydb.cursor()
        myCursor.execute("CREATE DATABASE bookmarks")
        myCursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255), url VARCHAR(255), notes VARCHAR(255))""")



# Get all bookmarks and prints them
def getBookmarks():
    myCursor.execute("SELECT * FROM bookmarks ORDER BY name")
    bookmarks = myCursor.fetchall()
    for x in bookmarks:
        print(x)


# Add a bookmark to the database
def addBookmark():
    sql = "INSERT INTO bookmarks (name, url, notes) VALUES (%s, %s, %s)"
    name = str(input("Enter name of bookmark: "))
    url = str(input("Enter url of bookmark: "))
    notes = str(input("Notes to add to bookmark: "))

    val = (name, url, notes)
    myCursor.execute(sql, val)
    mydb.commit()
    print("\nBookmark Added.")


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


if __name__ == '__main__':
    active = True
    actions = {
        "list bookmarks": getBookmarks,
        "add bookmark": addBookmark,
        "delete bookmark": deleteBookmark,
        "exit": exit
    }
    setup()

    while active:
        try:
            print("\n\nActions avalible: List Bookmarks, Add Bookmark, Delete Bookmark, Exit")
            action = str(input(">>> ")).lower()
            actions[action]()

        except KeyError:
            pass




