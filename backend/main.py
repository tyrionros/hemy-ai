from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="D365 Field Service Copilot Backend",
    description="API for the Dynamics 365 Field Service Copilot.",
    version="0.1.0"
)

# Pydantic models for request and response
class ChatRequest(BaseModel):
    message: str
    user_token: str # This will be the Entra ID token from the frontend

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def read_root():
    """A simple endpoint to verify that the service is running."""
    return {"message": "D365 Field Service Copilot backend is running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    The main endpoint for handling chat messages from the user.
    """
    # For now, we will just echo the message back.
    # In the future, this is where we will:
    # 1. Use the user_token to make a call on behalf of the user.
    # 2. Call an LLM to translate the natural language `request.message` to a Dataverse query.
    # 3. Execute the query against Dataverse.
    # 4. Format the result and return it.

    print(f"Received token: {request.user_token[:30]}...") # Log first 30 chars for verification
    
    return ChatResponse(reply=f"You said: '{request.message}'")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

