import mysql.connector
from psycopg2 import sql


class ConfigError(Exception):
    pass

class authenticate:
    def __init__(self) -> None:
        """
        Opens a auth.config file in the current directory
        and checks if it has all the required values
        """

        self.auth = {
        "host": "",
        "user": "",
        "password": ""
        }

        authParam = [
            "host=",
            "database=",
            "user=",
            "password="
        ]
        
        file = open("auth.config").read()
        authItems = file.split("\n")
        authSplit = []

        for (auth, item) in zip(authParam, authItems):
            if auth in item:
                authSplit.append(item.split("=")[1])

            else:
                raise ConfigError("Config file not configured correctly")

        self.auth["host"] = authSplit[0]
        self.database = authSplit[1]
        self.auth["user"] = authSplit[2]
        self.auth["password"] = authSplit[3]


    def createDatabase(self) -> None:
        """
        Create the database to store the bookmarks
        and creates the cursor to execute commands
        """

        try:
            # Tries to open the database with bookmarks in it
            self.db = mysql.connector.connect(**self.auth, database=self.database)
            self.cursor = self.db.cursor()

        except mysql.connector.errors.ProgrammingError as error:
            if "1049" in str(error):
                # If there is no database then create a database
                self.db = mysql.connector.connect(**self.auth)

                self.cursor = self.db.cursor()
                self.cursor.execute("CREATE DATABASE %s", (self.database, ))
                self.cursor.execute("USE %s", (self.database, ))

            else:
                raise error


    def createBookmarkTable(self) -> None:
        """
        Create the table bookmarks in the database 
        if it doesn't exist. If it does exist, checks
        to ensure the table has all required columns
        """
        COLUMNS = ("name", "url", "notes")

        try:
            self.cursor.execute("""CREATE TABLE bookmarks (id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255), url VARCHAR(255), notes VARCHAR(255))""")

        except mysql.connector.ProgrammingError as error:
            if "1050" in str(error):

                # Get all the columns and check whether the existing table has all required columns
                self.cursor.execute("DESCRIBE bookmarks")
                tableColumns = [x[0] for x in self.cursor.fetchall()]
                validTable = set(COLUMNS).difference(tableColumns)
            
                # If it doesn't then add each missing column to the table
                if validTable != []:
                    for column in validTable:
                        self.cursor.execute("ALTER TABLE bookmarks ADD COLUMN %s %s",
                        sql.Identifier(column),
                        sql.Identifier(COLUMNS[column]))