import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
from llms import llm
from states import StateIn, Book, ChapterTitleList, Chapter, TOC
from utils import read_google_sheet, generate_books_with_limited_overlap

load_dotenv()


def read_sheet(state: StateIn) -> StateIn:
    """
    Read a sheet from an Excel file and convert it to JSON.
    Args:
            state (StateIn)
    Returns:
            StateIn: The updated state with the chapters data.
    """
    sheet_id = state["sheet_id"]
    state["chapter_list"] = read_google_sheet(sheet_id=sheet_id)
    return state


def generate_combinations(state: StateIn) -> StateIn:
    structed_book: list[Book] = []
    unstructured_books = []
    books_list = generate_books_with_limited_overlap(
        chapters=state["chapter_list"], 
        r=state["r_chapters"], 
        max_docs=state["max_tokens"], 
        min_diff=state["min_diff"]
    )
    for books in books_list:
        book = Book(chapters=books)
        unstructured_books.append(books)
        structed_book.append(book)

    state["books"] = structed_book
    print(structed_book)
    return state


def generate_book(state:StateIn) -> StateIn:
    book = state["books"][0]
    manuscript_text = "\n\n".join([ch["chapter_content"] for ch in book])
    print(manuscript_text)
    

    # Shared context
    instructions = f"""
    This is the original manuscript to be expanded and edited:\n\n{manuscript_text}
    """

    # --- Define Agents ---
    expander = Agent(
        role="Content Expander",
        goal="Expand the manuscript to 10,000 words, maintain deep philosophical tone",
        backstory="An eloquent writer with a knack for expanding brief content into long-form philosophical prose.",
        llm=llm,
    )

    titler = Agent(
        role="Chapter Titler",
        goal="Extract quotes from each paragraph to use as chapter titles",
        backstory="A literary analyst who extracts compelling quotes and repurposes them creatively.",
        llm=llm,
    )

    preface_writer = Agent(
        role="Preface Writer",
        goal="Compose a suitable preface that introduces the manuscript naturally",
        backstory="A seasoned editor who writes introductory prefaces for nonfiction works.",
        llm=llm,
    )

    bonus_chapter_writer = Agent(
        role="Bonus Chapter Writer",
        goal="Write 3 additional chapters: 'Who Should Read This Book', 'Structure of This Book', 'How to Use This Book'",
        backstory="An instructional writing specialist who helps readers navigate complex content.",
        llm=llm,
    )

    bio_writer = Agent(
        role="Author Bio Writer",
        goal="Write a compelling author's biography from provided facts",
        backstory="A ghostwriter who crafts bios for thought leaders and executives.",
        llm=llm,
    )

    toc_writer = Agent(
        role="Table of Contents Writer",
        goal="Create a TOC using the generated chapter titles",
        backstory="An editorial assistant skilled in formatting structured content for publication.",
        llm=llm,
    )

    title_suggester = Agent(
        role="Title Suggester",
        goal="Suggest 3 provocative titles for the book",
        backstory="A copywriter who specializes in emotionally resonant, psychologically provocative titles.",
        llm=llm,
    )

    # --- Define Tasks ---
    expand_task = Task(
        description="Expand the manuscript to ~10,000 words with deep, philosophical yet modern tone.",
        agent=expander,
        expected_output="Expanded manuscript text chapterwise",
    )

    title_task = Task(
        description=f"Extract one quote from each paragraph of the original text to use as chapter titles. Here is the original manuscript - {manuscript_text}",
        context=[expand_task],
        agent=titler,
        expected_output="List of quote-based chapter titles",
        output_json=ChapterTitleList,
    )

    preface_task = Task(
        description="Write a preface that naturally introduces readers to the content of the book.",
        agent=preface_writer,
        expected_output="Preface text",
    )

    extra_chapter_task = Task(
        description="Write 3 additional chapters: 'Who Should Read This Book' (~700 words), 'Structure of This Book' (~700 words), 'How to Use This Book' (~700 words)",
        agent=bonus_chapter_writer,
        expected_output="Three new chapters",
        output_json=list[Chapter]
    )

    bio_task = Task(
        description=(
            "Write this author bio:\n"
            "'The author of this book has extensive experience in startups and international public companies, "
            "possesses deep insights into organizational operations, and specializes in resolving complex organizational dilemmas. "
            "Their professional background spans public companies in the United States and Germany, and they have held key positions "
            "at various leading corporations, excelling in general management, organizational transformation, and rapid expansion. "
            "Currently, the author provides management consulting services for senior executives and CEOs.'"
        ),
        agent=bio_writer,
        expected_output="Author biography",
    )

    toc_task = Task(
        description="Using the chapter titles generated from quotes, generate a formatted table of contents.",
        agent=toc_writer,
        expected_output="Formatted table of contents",
        output_json=TOC
    )

    suggest_titles_task = Task(
        description="Suggest 3 book titles that are provocative, direct, colloquial, and evoke psychological fears or emotions.",
        agent=title_suggester,
        expected_output="3 book title suggestions as a list of strings ordered by most recommended to least",
        output_json=list[str]

    )

    # --- Create and Run Crew ---
    crew = Crew(
        agents=[
            expander,
            titler,
            preface_writer,
            bonus_chapter_writer,
            bio_writer,
            toc_writer,
            title_suggester,
        ],
        tasks=[
            expand_task,
            title_task,
            preface_task,
            extra_chapter_task,
            bio_task,
            toc_task,
            suggest_titles_task,
        ],
        verbose=True,
        process=state.get("parallel", False)
        is False,  # default sequential unless you override
    )

    results = crew.kickoff(inputs={"context": instructions})

    # --- Return updated state ---
    state["expanded_book"] = {
        "manuscript": results[0],
        "chapter_titles": results[1],
        "preface": results[2],
        "additional_chapters": results[3],
        "bio": results[4],
        "table_of_contents": results[5],
        "title_options": results[6],
    }

    return state


def expand_chapter(state: StateIn) -> StateIn:
    pass


def generate_extras(state: StateIn) -> StateIn:
    pass
