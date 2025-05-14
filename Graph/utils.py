import os
import json
import pandas as pd
import logging
import googleapiclient
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
load_dotenv()
import random
from itertools import combinations
from typing import List, Dict
from states import Chapter, Book

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

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
	json_data = df.to_json(orient='columns')
	return json_data

def read_google_sheet():
	"""
	Read a Google Sheet and convert it to JSON (needs cred.json).
	Returns:
		str: The generated JSON.
	"""
	# sheet = client.open("BookExample").sheet1
	sheet = client.open_by_key(SHEET_ID).sheet1

	data = sheet.get_all_records()
	chapters = []
	for row in data:
		try:
			chapter = Chapter(**row)
			chapters.append(chapter)
		except Exception as e:
			print(f"Skipping invalid row: {row} - Error: {e}")
	# print(chapters)
	return chapters


import random
from typing import List, Set, Tuple
from pydantic import BaseModel

class Chapter(BaseModel):
    chapter_title: str
    chapter_content: str

def generate_unique_books(chapters: List[Chapter], r: int, k: int) -> List[List[Chapter]]:
    """
    Generate k unique books, each with r chapters selected from the input list.
    Ensure each book differs by at least 1 chapter from every other.
    
    Args:
        chapters: List of Chapter models.
        r: Number of chapters per book.
        k: Number of books to generate.

    Returns:
        A list of books, each book is a list of r Chapter models.
    """
    if r > len(chapters):
        raise ValueError("r cannot be greater than the total number of chapters")

    seen: Set[Tuple[int, ...]] = set()
    books: List[List[Chapter]] = []

    attempts = 0
    max_attempts = 10000

    while len(books) < k and attempts < max_attempts:
        combo = tuple(sorted(random.sample(range(len(chapters)), r)))
        if combo in seen:
            attempts += 1
            continue

        # Ensure each combo differs from all others by at least one chapter
        if all(len(set(combo) ^ set(existing)) >= 1 for existing in seen):
            seen.add(combo)
            book = [chapters[i] for i in combo]
            books.append(book)

        attempts += 1

    if len(books) < k:
        raise RuntimeError(f"Could only generate {len(books)} books with r={r}, k={k}. Try reducing k or r.")
    # print(books)
    return books


def generate_books_with_limited_overlap(chapters: List[Chapter], r: int, k: int) -> List[List[Chapter]]:
    """
    Generate k books of r chapters each, ensuring no more than 1 overlapping chapter between any pair.
    
    Args:
        chapters: List of Chapter models.
        r: Chapters per book.
        k: Number of books.
    
    Returns:
        List of k books (each is a list of r Chapter objects).
    """
    if r > len(chapters):
        raise ValueError("r cannot be greater than the number of available chapters")
    
    books: List[List[Chapter]] = []
    used_chapter_sets: List[Set[int]] = []

    chapter_indices = list(range(len(chapters)))
    max_attempts = 10000
    attempts = 0

    while len(books) < k and attempts < max_attempts:
        candidate_indices = set(random.sample(chapter_indices, r))

        # Check overlap constraint: max 1 overlap with any existing book
        is_valid = all(len(candidate_indices & used) <= 1 for used in used_chapter_sets)

        if is_valid:
            books.append([chapters[i] for i in candidate_indices])
            used_chapter_sets.append(candidate_indices)

        attempts += 1

    if len(books) < k:
        raise RuntimeError(f"Only generated {len(books)} books with the required overlap constraint. Try reducing k or r.")

    return books

if __name__ == "__main__":
	chapters = read_google_sheet()
    
	structed_book:List[Book] = []

	books = generate_books_with_limited_overlap(chapters, 3, 5)
	for i, book in enumerate(books):
		print(f"📘 Book {i+1}:")
		x = Book(chapters=book, book_title=f"Book {i+1}")
		structed_book.append(x)

print(structed_book)