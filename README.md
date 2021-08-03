# Chronos Bookmark Database (Ongoing)
MySql database that stores bookmarks. Has a command line interface, using python as a backend

## Features
- List all bookmarks
- Add bookmarks
- Delete bookmarks
- Edit bookmarks
- Search for bookmarks
- Import from html file

## Features to come
- Filters

## Installation
Clone the git repository
`git clone https://github.com/PatrickTLuu/BookmarkDatabase.git`

Use a text editor to create a auth.config file in the repository
```bash
cd BookmarkDatabase
vim auth.config
```

Configure mysql database authentication
```conf
database=ChronosBookmarks
username=       
password=   
```      

### Library Dependencies
- MySQL Connector
- Argparse
- HTML Parser
