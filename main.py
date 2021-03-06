from dataframe import *
from datascraper import *

if __name__ == "__main__":
    # SETTINGS #
    DOWNLOAD_FILES = True # download pdfs and image files
    DOWNLOADS_FOLDER = ".\\downloads" # output directory for downloads
    GO_TO_NEXT_PARCEL = True # automatically continue to next parcel
    ENTRY_LIMIT = 1000 # Stop after certain number of entries. If None - go on forever
    START_URL = "http://qpublic9.qpublic.net/la_orleans_display.php?KEY=1125-PERDIDOST&"
    END_WHEN_DUPLICATE = True # Assume that a duplicate entry means that all entries have been parsed

    scraper = Scraper(DOWNLOADS_FOLDER, DOWNLOAD_FILES, GO_TO_NEXT_PARCEL, ENTRY_LIMIT, END_WHEN_DUPLICATE)
    scraper.ReadWebPage(START_URL)