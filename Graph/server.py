#FastAPI server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import uvicorn
import os
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
async def invoke():
	"""
	Invoke the graph and return the result.
	"""
	result = graph.invoke()

	return {"result": result}
		
if __name__ == "__main__":
		uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True)