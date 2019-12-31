from dataframe import *
from datascraper import *

if __name__ == "__main__":
    scraper = Scraper("downloads")
    scraper.ReadWebPage("http://qpublic9.qpublic.net/la_orleans_display.php?KEY=1125-PERDIDOST&")