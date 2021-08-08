import argparse
import sys
import commands


# Initial parser and subparser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title = "sub commands")


# Creates sub commands
class subParsers():
    def __init__(self, name, helpStr, args) -> None:
        self = subparsers.add_parser(name, help=helpStr)

        for arg in args:
            if arg[0][0] == "-":
                self.add_argument(arg[0], arg[1], help=arg[2], metavar="")

            else:
                self.add_argument(arg[0], help=arg[1])


# All sub commands
lsCmd = subParsers("ls", "list bookmarks", [])
addCmd = subParsers("add", "add a bookmark", [("name", "name of bookmark"), ("url", "url of bookmark"), ("notes", "notes to add")])
editCmd = subParsers("edit", "edit a bookmark", [("name", "name of bookmark"), ("column", "column change"), ("value", "new Value")])
deleteCmd = subParsers("delete", "delete a bookmark", [("name", "name of bookmark")])
searchCmd = subParsers("search", "search for bookmark", [("name", "name of bookmark")])
importCmd = subParsers("import", "import bookmarks from html file", [("path", "path to html file")])



if __name__ == '__main__':

    parser.parse_args()

    actions = {
        "ls": [commands.listBookmarks, object],
        "search": [commands.search, object],
        "add": [commands.addBookmark, str],
        "edit": [commands.editBookmark, str],
        "delete": [commands.deleteBookmark, str],
        "import": [commands.importBookmarks, str]
    }

    # Call function from commands
    command = str(sys.argv[1])
    toPrint = actions[command][0](*sys.argv[2:])


    # If the function returned a tuple or list to be printed, print each value
    if actions[command][1] == object:
        for x in toPrint.bookmarks:
            print("\n{}".format(x))
        

    # Otherwise just print returned value
    else:
        print("\n{}".format(toPrint))


print()
