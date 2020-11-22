#!/usr/bin/env python

from goodsreads_scraper.Browser import Browser
# import needed libraries
from goodsreads_scraper.Writer import Writer
from bs4 import BeautifulSoup

from goodsreads_scraper.Tools import id_from_url, read_books, get_digits


# A class to Search then Scrape lists and books from GoodReads.com
class Books:
    def __init__(self, path=None, arabic=True):
        self.arabic = arabic
        # Browsing and writing managers
        self.br = Browser()
        self.wr = Writer(path) if path else Writer()
        # An array for scrapped books
        self._books_ids = []

    # Append an external books ids array to local array
    def append_books(self, books_ids):
        # Loop through sent books ids
        for book_id in books_ids:
            # Only append id if it's not stored already
            if book_id not in self._books_ids:
                self._books_ids.append(book_id)

    # Scrape books and write them to a file (browse is: list, lists, author or shelf)
    def output_books(self, keyword=None, browse="list", file_name="books"):
        self.wr.open(file_name, "w+")
        # Get books if keyword is provided, otherwise output stored books
        books_ids = self.get_books(keyword, browse) if keyword else self._books_ids
        # Loop through book ids and write them
        for book_id in books_ids:
            self.wr.write(book_id)
        self.wr.close()

    def output_books_editions(self, books_ids=None, file_name="editions"):
        skip = len(read_books(file_name))
        self.wr.open(file_name, "a+")
        # Loop through book ids and write their editions id
        for book_id in books_ids[skip:] or self._books_ids[skip:]:
            editions_id = self.get_book_editions_id(book_id)
            # Editions id is None when page refuses to load
            if editions_id is None: return self.wr.close()
            # Write editions id to file if it loads correctly
            self.wr.write(editions_id or "-"*7)
            # Display book id and editions id
            print(f"Book ID:\t{book_id:<15}Book Editions ID:\t{editions_id or ''}")
        self.wr.close()
        return True

    def output_books_edition_by_language(self, editions_ids, lang="Arabic", file_name="ara_books"):
        skip = len(read_books(file_name))
        self.wr.open(file_name, "a+")
        # Loop through book ids and write their editions id
        for editions_id in editions_ids[skip:]:
            books_ids = self.get_book_edition_by_language(editions_id, lang) if editions_id.isdigit() else ''
            # Editions id is None when page refuses to load
            if books_ids is None: return self.wr.close()
            # Write editions id to file if it loads correctly
            self.wr.write(books_ids or "-"*7)
            # Display book id and editions id
            print(f"Book Editions ID:\t{editions_id:<15}Books IDs:\t{books_ids or ''}")
        self.wr.close()
        # Open a new file to move done list to it
        self.wr.open(file_name + "_list")
        # Loop through previously scraped editions ids
        for line in read_books(file_name):
            # If line isn't empty
            if line != "-"*7:
                # Write each book edition id in a separate line
                [self.wr.write(id_) for id_ in line.split(',')]
        self.wr.close()
        return True

    # Main function to scrape books ids
    def get_books(self, keyword, browse="list"):
        # Get lists in search list if searching
        if browse == "lists":
            keywords = self._get_lists(keyword.replace(' ', '+'))
            browse = "list"
        # Otherwise, it's a single "list" or "shelf"
        else:
            keywords = [
                str(key) for key in (
                    keyword if isinstance(keyword, list) else [keyword]
                )]
        try:
            # Loop through all lists
            for keyword in keywords:
                # Open each list url
                self.br.open_page(keyword, browse)
                # Scrape pages until there's no next page
                while True:
                    self._scrape_list("book", self._books_ids)
                    if not self.br.goto_next_page():
                        break
        except Exception as e:
            print("Couldn't go to next page:", e)
        finally:
            return self._books_ids

    def get_book_editions_id(self, book_id):
        self.br.open("/book/show/", book_id)
        return self.br.editions_id()

    def get_book_details(self, book_id):
        self.br.open("/book/show/", book_id)
        try:
            return self.br.book_details(book_id)
        except ValueError:
            self.br.open("/book/show/", book_id)
            return self.br.book_details(book_id)

    def get_book_cover(self, book_id):
        self.br.open("/book/show/", book_id)
        try:
            return self.br.book_cover()
        except ValueError:
            self.br.open("/book/show/", book_id)
            return self.br.book_cover()

    def get_book_edition_by_language(self, editions_id, lang):
        self.br.open_book_editions(editions_id)
        soup = BeautifulSoup(self.br.page_source, "lxml").find(class_="workEditions")
        if not soup: return None
        editions = []
        for details in soup.find_all(class_="editionData"):
            language, rating = [row.find(class_="dataValue") for row in details.find_all(class_="dataRow")[-3:-1]]
            if language.text.strip() == lang:
                reviewers = get_digits(rating.find("span").text)
                if reviewers > 50:
                    editions.append(id_from_url.match(details.find(class_="bookTitle")["href"]).group(1))
        return ','.join(editions)

    # Main function to scrape lists ids
    def _get_lists(self, keyword):
        lists = []
        # Open GoodReads' lists search url
        self.br.open_list_search(keyword)
        # Scrape all result pages
        while True:
            self._scrape_list("list", lists)
            # Go to next page if there's one, otherwise break
            if not self.br.goto_next_page():
                break
        return lists

    # Scrape a single search results page
    def _scrape_list(self, title, array):
        soup = BeautifulSoup(self.br.page_source, "lxml").find(class_="tableList")
        if not soup: return None
        for book in soup.find_all("tr"):
            if self.arabic or get_digits(book.find(class_="minirating").text.split("—")[1]) > 1000:
                try:  # Get id from url
                    id_ = id_from_url.match(book.find(class_=title + "Title")["href"]).group(1)
                except Exception:
                    print("Couldn't extract Book Id from URL")
                    continue
                # Extract and store unique id from link
                if id_ not in array:
                    array.append(id_)
                    print(f"{title.capitalize()} {id_:<10}count:\t{len(array)}")
