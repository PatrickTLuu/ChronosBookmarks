from html.parser import HTMLParser

isBookmark = [False, False]
allBookmarks = []

class BookmarkHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "dt":
            isBookmark[0] = True
        elif tag == "a":
            isBookmark[1] = True

        if isBookmark[0] and isBookmark[1]:
            for attr in attrs:
                if attr[0] == "href":
                    allBookmarks.append([attr])

    def handle_data(self, data):
        if isBookmark[0] and isBookmark[1]:
            last = len(allBookmarks)-1
            allBookmarks[last].append(data)
            isBookmark[0] = False
            isBookmark[1] = False



