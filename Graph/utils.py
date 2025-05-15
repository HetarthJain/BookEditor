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
    # print("chapss---------------------------\n",given_chasps)
    return chapters

def generate_books_with_limited_overlap(
    chapters: List[Chapter], 
    r: int = 3, 
    max_docs: int = 5, 
    min_diff: int = 1
) -> List[List[Chapter]]:
    """
    Generate k books of r chapters each, ensuring no more than 1 overlapping chapter between any pair.

    Args:
        chapters: List of Chapter models.
        r: Chapters per book.
        max_docs: Number of books.
        min_diff: minimum number of common chapters between combinations.

    Returns:
        List of max_docs books (each is a list of r Chapter objects).
    """
    if r > len(chapters):
        raise ValueError("r cannot be greater than the number of available chapters")

    books: List[Book] = []
    used_chapter_sets: List[Set[int]] = []

    chapter_indices = list(range(len(chapters)))
    max_attempts = 10000
    attempts = 0

    while len(books) < max_docs and attempts < max_attempts:
        candidate_indices = set(random.sample(chapter_indices, r))

        # Check overlap constraint: max 1 overlap with any existing book
        is_valid = all(len(candidate_indices & used) <= 1 for used in used_chapter_sets)

        if is_valid:
            books.append([chapters[i] for i in candidate_indices])
            used_chapter_sets.append(candidate_indices)

        attempts += 1

    if len(books) < max_docs:
        raise RuntimeError(
            f"Only generated {len(books)} books with the required overlap constraint. Try reducing k or r."
        )

    return books


if __name__ == "__main__":
    chapters = read_google_sheet(sheet_id=SHEET_ID)
    print("hi----------------------------\n",chapters)

    books = generate_books_with_limited_overlap(chapters, 3, 5, 1)
    for i, book in enumerate(books):
        print(f"📘 Book {i + 1}:")
        print(book)