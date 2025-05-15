# FastAPI server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import uuid
from dotenv import load_dotenv
from graph import graph

load_dotenv()

PORT = os.getenv("PORT", 8000)

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/invoke")
async def invoke(payload: dict):
    """
    Invoke the graph and return the result.
    """
    gpt_prompt = payload.get("gpt_prompt")
    openai_api_key = payload.get("openai_api_key")
    output_lang = payload.get("output_lang")
    max_tokens = payload.get("max_tokens")
    max_docs = payload.get("max_docs")
    min_diff = payload.get("min_diff")
    r_chapters = payload.get("r_chapters")
    mode = payload.get("mode")
    openai_api_key = openai_api_key

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    output = graph.invoke(
        input={
            "messages": [("human", gpt_prompt)],
            "gpt_prompt": gpt_prompt,
            "openai_api_key": openai_api_key,
            "output_lang": output_lang,
            "max_tokens": max_tokens,
            "max_docs": max_docs,
            "min_diff": min_diff,
            "r_chapters": r_chapters,
            "mode": mode,
        },
        config=config,
        stream_mode="values",
    )
    out_sheet = output.get("out_sheet")

    return {"message":f"{max_docs} Books are created and saved in a google docs. Here is the google sheet - {out_sheet}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True)
