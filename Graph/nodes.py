import os
from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, Crew, Task

from llms import llm
from states import *
from utils import *

def read_sheet(state: StateIn) -> StateIn:
	"""
	Read a sheet from an Excel file and convert it to JSON.
	Args:
		state (StateIn)
	Returns:
		StateIn: The updated state with the chapters data.
	"""
	state["chapter_list"] = read_google_sheet()
	return state

def generate_combinations(state: StateIn) -> StateIn:
	structed_book: List[Book] = []
	books_list = generate_books_with_limited_overlap(state["chapter_list"], state["r"], state["k"])
	for books in books_list:
		book = Book(chapters=books)
		structed_book.append(book)

	state["books"] = structed_book
	print(structed_book)
	return state

def expand_chapter(state: StateIn) -> StateIn:
	pass

def generate_extras(state: StateIn) -> StateIn:
	pass

