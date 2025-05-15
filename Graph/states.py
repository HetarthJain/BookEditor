from langgraph.graph import MessagesState
from typing import Any, Dict, List, Optional, Tuple, Annotated
import operator
from pydantic import BaseModel, Field, ConfigDict


class ChapterTitleList(BaseModel):
    chapter_titles: list[str]
class TOC:
    preface: str
    who_should_read_this_book: str
    structure_of_book: str
    how_to_use_this_book: str
    bio: str
    chapter_list: ChapterTitleList


class Chapter(BaseModel):
	chapter_title: str
	chapter_content: str

class Book(BaseModel):
	book_title: str
	chapters: List[Chapter]
	model_config = ConfigDict(arbitrary_types_allowed=True)

class GeneratedBook(BaseModel):
	book_titles: list[str]
	preface: str
	additional_chapters: list[Chapter]
	bio: str
	table_of_contents: dict
	chapters: list[Chapter]


class StateIn(MessagesState):
	sheet_id: str
	books: List[Book]
	mode: str 
	r_chapters: int
	total_docs: int
	min_diff: int
	max_tokens: int
	openai_api_key: str
	output_lang: str
	gpt_prompt: str
	books_generated: Annotated[List[Book], operator.add]
	chapter_list: List[Chapter]

class StateOut(MessagesState):
	out_sheet:str
	books_generated: Annotated[List[Book], operator.add]