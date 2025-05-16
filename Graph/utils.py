import os
import json
import pandas as pd
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from itertools import combinations
from typing import List, Set, Tuple
from states import Chapter, Book
from dotenv import load_dotenv

load_dotenv()

# Define the scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Authenticate using the JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
client = gspread.authorize(creds)

SHEET_ID = os.getenv("SHEET_ID")


def excel_to_json(file_path):
    """
    Convert an Excel file to a JSON file.
    Args:
            file_path (str): The path to the Excel file.
    Returns:
            str: The generated JSON.
    """
    # Read the Excel file
    df = pd.read_excel(file_path)
    json_data = df.to_json(orient="columns")
    return json_data

def read_google_sheet(sheet_id):
    """
    Read a Google Sheet and convert it to JSON (needs cred.json).
    Returns:
            str: The generated JSON.
    """
    # sheet = client.open("BookExample").sheet1
    sheet = client.open_by_key(sheet_id).sheet1

    data = sheet.get_all_records()
    chapters = []
    given_chasps = []
    for row in data:
        try:
            given_chasps.append(row)
            chapter = Chapter(**row)
            chapters.append(chapter)
        except Exception as e:
            print(f"Skipping invalid row: {row} - Error: {e}")
    # print("read_data_util:\n",chapters)
    return chapters

def generate_books_with_limited_overlap1(
    chapters: List[Chapter], r: int = 3, max_docs: int = 3, max_overlap: int = 1
) -> List[Book]:
    """
    Generate `max_docs` Book objects with `r` Chapters each,
    ensuring no two books share more than `max_overlap` chapters.

    Args:
        chapters: List of Chapter Pydantic objects.
        r: Number of chapters per book.
        max_docs: Total number of books to generate.
        max_overlap: Maximum number of overlapping chapters allowed between any pair of books.

    Returns:
        List of `Book` objects.

    Raises:
        RuntimeError: If unable to generate enough valid books under constraints.
    """
    if r > len(chapters):
        raise ValueError("r cannot be greater than the number of available chapters")
    if max_overlap >= r:
        raise ValueError("max_overlap must be less than r")

    books: List[Book] = []
    used_chapter_sets: List[Set[int]] = []
    chapter_indices = list(range(len(chapters)))

    attempts = 0
    max_attempts = 5

    while len(books) < max_docs and attempts < max_attempts:
        candidate_indices = set(random.sample(chapter_indices, r))

        # Ensure overlap constraint is satisfied with all existing books
        if all(
            len(candidate_indices & used) <= max_overlap for used in used_chapter_sets
        ):
            selected_chapters = [chapters[i] for i in candidate_indices]
            book_title = f"Book {len(books) + 1}"
            books.append(Book(book_title=book_title, chapters=selected_chapters))
            used_chapter_sets.append(candidate_indices)

        attempts += 1

    if len(books) < max_docs:
        raise RuntimeError(
            f"Only generated {len(books)} books with the required overlap constraint. "
            f"Try increasing the total number of chapters, decreasing r, or increasing max_overlap."
        )
    # print("overlap:\n", books)
    return books

if __name__ == "__main__":
    chapters = read_google_sheet(sheet_id=SHEET_ID)
    # print("hi----------------------------\n",chapters)

    books = generate_books_with_limited_overlap1(chapters, 3, 5, 1)
    for i, book in enumerate(books):
        print(f"📘 Book {i + 1}:")
        print(book)