from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

print(os.getenv("OPENAI_API_KEY"))

llm_gpt = ChatOpenAI(
	model="gpt-4o",
	temperature=0,
	top_p=0.2,
) 

# llm_gemini = ChatVertexAI(
# 	model="gemini-2.0-flash-001",
# 	temperature=0,
# 	top_p=0.2,
# )

llm = llm_gpt
