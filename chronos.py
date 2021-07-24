import argparse
import sys
import commands


# Initial parser and subparser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title = "sub commands")


# Creates sub commands
class subParsers():
    def __init__(self, name, helpStr, args):
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

    # Run setup
    commands.setup()
    parser.parse_args()

    actions = {
        "ls": commands.listBookmarks,
        "search": commands.searchBookmark,
        "add": commands.addBookmark,
        "edit": commands.editBookmark,
        "delete": commands.deleteBookmark,
        "import": commands.importBookmarks,
    }

    # Call function from commands
    toPrint = actions[str(sys.argv[1])](*sys.argv[2:])


    # If the function returned a tuple or list to be printed, print each value
    if isinstance(toPrint[1], (list, tuple)):
        for x in toPrint[1]:
            print("\n{}".format(x))

    # Otherwise just print returned value
    else:
        print("\n{}".format(toPrint[1]))

    print("\n")
