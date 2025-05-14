from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from nodes import *
from states import *


memory = MemorySaver()

graph_builder = StateGraph(state_schema=StateIn, output=StateOut)
# Nodes
graph_builder.add_node("read_sheet", read_sheet)
graph_builder.add_node("generate_combinations", generate_combinations)



# Edges
graph_builder.add_edge(START, read_sheet)

# Compiled graph
graph = graph_builder.compile(checkpointer=memory, debug=False)

