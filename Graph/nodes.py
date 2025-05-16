import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
from llms import llm
from typing import List
from states import StateIn, Book, ChapterTitleList, Chapter, TOC, ExpandedChapter, Extras
from utils import read_google_sheet, generate_books_with_limited_overlap1

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
    books_list = generate_books_with_limited_overlap1(
        chapters=state["chapter_list"],
        r=state["r_chapters"],
        max_docs=state["max_docs"],
        max_overlap=state["max_overlap"],
    )
    for i, books in enumerate(books_list):
        book = Book(chapters=books.chapters, book_title=f"Book {i + 1}:")
        unstructured_books.append(books)
        structed_book.append(book)

    state["books"] = structed_book
    # print(structed_book)
    return state


def generate_book(state:StateIn) -> StateIn:

    # --- Define Agents and Task functions ---
    expander_agent = Agent(
        role="Philosophical Long-Form Expansion Expert",
        goal="Expand brief chapters into rich, deep, long-form philosophical content.",
        backstory=(
            "You are a world-class philosophical writer who excels at transforming short insights "
            "into profound, expansive texts with emotional depth, clarity, and elegance."
        ),
        llm=llm,
    )

    def create_expansion_task(chapter: Chapter) -> Task:
        return Task(
            description=(
                f"Expand the following chapter into a deeply philosophical long-form essay of around 1,500 words.\n\n"
                f"### Chapter Title: {chapter.chapter_title}\n\n"
                f"### Original Content:\n{chapter.chapter_content}\n\n"
                "Ensure a modern tone, reflective insights, logical flow, and high-quality transitions. "
                "Avoid academic language or redundancy. Every paragraph must be engaging and valuable."
            ),
            expected_output="Expanded long-form version of the chapter, with keys chapter_title and chapter_content as provided in output_json format.",
            agent=expander_agent,
            output_json=ExpandedChapter
        )

    def run_crews_in_loop(chapters: List[Chapter]):
        expanded_chapters = []
        for ch in chapters:
            expander_task = create_expansion_task(ch)
            crew = Crew(
                agents=[expander_agent],
                tasks=[expander_task],
                # verbose=True
            )
            results = crew.kickoff()
            print("RESULT:::-----------------------\n", results["chapter_title"])
            expanded_chapters.append(
                ExpandedChapter(
                    chapter_title=ch.chapter_title,
                    expanded_content=results["expanded_content"],
                )
            )
        return expanded_chapters


    # --- Run for all books ---
    for book in state["books"]:
        print(f"Book {state['books'].index(book) + 1}:-----------------------------------------")
        # --- Run the crew in a loop to generate each chapter of a book ---
        expanded_chapters = run_crews_in_loop(book.chapters)
        book.chapters = expanded_chapters
        book.book_title = f"Book {state['books'].index(book) + 1}:"

    # print("BOOKS:::-----------------------\n", state["books"])
    return state


def generate_preface(state: StateIn) -> StateIn:
    preface_agent = Agent(
        role="Preface Writer",
        goal="Compose a suitable preface that introduces the manuscript naturally",
        backstory="A seasoned editor who writes introductory prefaces for nonfiction works.",
        llm=llm,
    )

    def create_prefece_task(book) -> Task:
        return Task(
            description=(f"""
                You are a preface writer. 
                You will be given a book with chapters.
                Generate a preface for the book, summarizing its themes and purpose.
                The preface should be engaging and set the tone for the reader.
                This is the expanded book: {book}
                """
            ),
            expected_output="Preface content.",
            agent=preface_agent,
        )
    
    for book in state["books"]:
        preface_task = create_prefece_task(book)
        preface_crew = Crew(
            agents=[preface_agent],
            tasks=[preface_task],
            # verbose=True
        )
        
        preface_results = preface_crew.kickoff()
        print("PREFACE--RESULT:::-----------------------\n", preface_results)
    return state


def generate_extras(state: StateIn) -> StateIn:
    extras_agent = Agent(
        role="Introductory Chapter Strategist & Reader Onboarding Specialist",
        goal=(
            "Craft compelling, clear, and thoughtfully structured introductory chapters—"
            "'Who Should Read This Book', 'Structure of This Book', and 'How to Use This Book'—"
            "to guide the reader with purpose and inspire engagement. Each chapter should be "
            "well-developed, engaging, and aligned with the book's tone and purpose. Each chapter should be around ~700 words long."
        ),
        backstory=(
            "You are a highly experienced instructional designer and non-fiction editor. "
            "You've helped bestselling authors create accessible entry points into deep and complex material. "
            "You specialize in crafting reader-friendly guidance, setting context, framing expectations, and inspiring curiosity. "
            "You know how to connect the reader to the material with clarity, empathy, and vision."
        ),
        llm=llm,
    )

    def create_extras_task(book: Book) -> Task:
        return Task(
            description=(
                f"""
You are given the full content of a structured non-fiction book titled "{book.book_title}" composed of the following chapters:

{[ch.chapter_title for ch in book.chapters]}

Your task is to write **three well-developed introductory chapters**:
1. **Who Should Read This Book** : Describe the ideal reader profile. Identify their problems, mindset, or goals. Help them self-identify and feel seen.
2. **Structure of This Book** : Explain how the book is organized, chapter by chapter. Reveal the thought process behind the structure and how it benefits the reader.
3. **How to Use This Book** : Provide practical guidance on how readers should approach the book. Should they read linearly or by topic? How should they take notes or reflect? Should they revisit sections?
Each section must be **engaging, clearly written, and tuned to the tone and purpose of the book**. Be instructive but not dry. Use a warm, confident, yet professional voice.
Each chapter should be around ~700 words long.
Return a dictionary like:
```json
{{
"who_should_read_this_book": "..."
"how_to_use_this_book": "..."
"structure_of_book": "..."
}}
```
            """
            ),
            expected_output="A dictionary with keys 'Who Should Read This Book', 'Structure of This Book', and 'How to Use This Book', and high-quality corresponding content as values.",
            agent=extras_agent,
            output_json=Extras
        )

    for book in state["books"]:
        extras_task = create_extras_task(book)
        extras_crew = Crew(
            agents=[extras_agent],
            tasks=[extras_task],
            # verbose=True
        )
        
        extras_results = extras_crew.kickoff()
        extras_results = extras_results.strip().replace("```","").replace("json","")
        print("Extras--RESULT:::-----------------------\n", extras_results)
    return state


def generate_bio(state: StateIn) -> StateIn:
    bio_agent = Agent(
        role="Author Bio Architect",
        goal="Craft a compelling, trust-building author bio that resonates deeply with the book's philosophical and professional themes.",
        backstory=(
            "You are an accomplished narrative strategist and editorial consultant. "
            "You specialize in transforming professional backgrounds into relatable and inspiring biographies. "
            "Your bios bridge the gap between expertise and human connection, making the author feel both credible and approachable."
        ),
        llm=llm,
    )

    def create_bio_task(book: Book) -> Task:
        author_info = (
            "The author of this book has extensive experience in startups and international public companies. "
            "They possess deep insights into organizational operations and specialize in resolving complex dilemmas. "
            "Their career spans executive roles in public companies across the United States and Germany. "
            "They have led major initiatives in general management, organizational transformation, and rapid growth. "
            "Currently, the author advises senior executives and CEOs as a management consultant. "
            f"This bio should reflect their relevance to the book titled '{book.book_title}' and its themes."
        )
        return Task(
            description=(
                f"""
Write a professional, engaging, and reader-resonant **author biography**.
It should be concise (150–200 words), written in third-person, and speak to the author’s **credibility, unique experience, and personal connection** to the book’s subject.

Author Info:
{author_info}

Output Format:
```json
{{
  "bio": "..."
}}
"""
            ),
            expected_output="A JSON dictionary with a single key 'bio' and the biography string as the value.",
            agent=bio_agent,
        )

    for book in state["books"]:
        bio_task = create_bio_task()
        bio_crew = Crew(
            agents=[bio_agent],
            tasks=[bio_task],
            # verbose=True
        )
        
        bio_results = bio_crew.kickoff()
        bio_results = bio_results.strip().replace("```","").replace("json","")
        print("Bio--RESULT:::-----------------------\n", bio_results)
    return state


def generate_toc(state: StateIn) -> StateIn:
    toc_agent = Agent(
        role="Table of Contents Creator",
        goal="Generate a structured table of contents for the book.",
        backstory=(
            "You are a seasoned editor and content strategist. "
            "You excel at creating clear, logical, and engaging tables of contents that guide readers through complex material."
        ),
        llm=llm,
    )

    def create_toc_task(book: Book) -> Task:
        return Task(
            description=(
                f"""
You are given the full content of a structured non-fiction book titled "{book.book_title}" composed of the following chapters:

{[ch.chapter_title for ch in book.chapters]}
Your task is to write a **Table of Contents** for the book.
The table of contents should include:
1. **Preface**: A brief introduction to the book.
2. **Who Should Read This Book**: A description of the ideal reader profile.
3. **Structure of This Book**: An explanation of how the book is organized, chapter by chapter.
4. **How to Use This Book**: Practical guidance on how readers should approach the book.
5. **Author Bio**: A brief biography of the author.
6. **Chapters**: A list of all chapters in the book.
The table of contents should be clear, engaging, and aligned with the book's tone and purpose.
Return a dictionary like:
```json
{{
"preface": "Preface",
"who_should_read_this_book": "Who Should Read This Book",
"structure_of_book": "Structure of This Book",
"how_to_use_this_book": "How to Use This Book",
"bio": "Author Bio",
"chapter_list": {{
  "chapter_titles": {book.chapters}
}}
}}
```
"""
            ),
            expected_output="A JSON dictionary with keys 'preface', 'who_should_read_this_book', 'structure_of_book', 'how_to_use_this_book', 'bio', and 'chapter_list' with high-quality corresponding content as values.",
            agent=toc_agent,
            output_json=TOC
        )
    for book in state["books"]:
        toc_task = create_toc_task(book)
        toc_crew = Crew(
            agents=[toc_agent],
            tasks=[toc_task],
            # verbose=True
        )
        
        toc_results = toc_crew.kickoff()
        toc_results = toc_results.strip().replace("```","").replace("json","")
        print("TOC--RESULT:::-----------------------\n", toc_results)

    return state


def write_doc():
    # Implement the logic to write the generated book content to a document or file from the state variables.
    pass
