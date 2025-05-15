from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from nodes import read_sheet, generate_combinations, generate_book
from states import StateIn, StateOut


memory = MemorySaver()

graph_builder = StateGraph(state_schema=StateIn, output=StateOut)
# Nodes
graph_builder.add_node("read_sheet", read_sheet)
graph_builder.add_node("generate_combinations", generate_combinations)
graph_builder.add_node("generate_book", generate_book)


# Edges
graph_builder.add_edge(START, "read_sheet")
graph_builder.add_edge("read_sheet", "generate_combinations")
graph_builder.add_edge("generate_combinations", "generate_book")
graph_builder.add_edge("generate_book", END)


# Compiled graph
graph = graph_builder.compile(checkpointer=memory, debug=False)
