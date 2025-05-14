from langgraph.graph import MessagesState
from typing import Any, Dict, List, Optional, Tuple
import operator
from pydantic import BaseModel, Field, ConfigDict



class Chapter(BaseModel):
	chapter_title: str
	chapter_content: str

class Book(BaseModel):
	book_title: str
	chapters: List[Chapter]
	model_config = ConfigDict(arbitrary_types_allowed=True)


class StateIn(MessagesState):
	sheet: str
	books: List[Book]
	r: int
	k: int
	chapter_list: List[Chapter]

class StateOut(MessagesState):
	out_sheet:str
	books_generated: List[Book]