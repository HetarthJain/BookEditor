import os
from dotenv import load_dotenv
from graph import graph

load_dotenv()

#inputs from web interface
max_docs = 3
min_diff = 1
r_chapters = 3
mode = "permutation"

max_tokens = 10000
openai_api_key = "your_openai_api_key"
output_lang = "en"
gpt_prompt = "Generate Book from given chapters."
sheet_id = os.getenv("SHEET_ID")

config = {"configurable": {"thread_id": "001"}}

output = graph.invoke( 
	input={
		"messages": [("human",gpt_prompt)],
		"gpt_prompt":gpt_prompt,
		"openai_api_key":openai_api_key,
		"output_lang": output_lang,
		"max_tokens":max_tokens,
		"max_docs":max_docs,
		"min_diff":min_diff,
		"r_chapters":r_chapters,
		"mode":mode,
		"sheet_id": sheet_id
	},
	config=config,
	stream_mode="values"
)

print(output)
