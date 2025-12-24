from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
import requests

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="D365 Field Service Copilot Backend",
    description="API for the Dynamics 365 Field Service Copilot.",
    version="0.1.0"
)

# --- Authentication ---
security = HTTPBearer()
TENANT_ID = os.getenv("AZURE_TENANT_ID")
AUDIENCE = os.getenv("AZURE_CLIENT_ID") # The backend's client ID
AUTH_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

# In a production app, you would cache this response.
jwks = requests.get(JWKS_URI).json()

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate the bearer token from the request."""
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            decoded_token = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=AUDIENCE,
                issuer=AUTH_AUTHORITY
            )
            return decoded_token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find appropriate key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- API Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# --- Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to verify that the service is running."""
    return {"message": "D365 Field Service Copilot backend is running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token_payload: dict = Depends(validate_token)):
    """
    The main endpoint for handling chat messages from the user.
    Requires a valid JWT bearer token.
    """
    user_name = token_payload.get("name", "Unknown User")
    print(f"Request from authenticated user: {user_name}")
    
    return ChatResponse(reply=f"{user_name}, you said: '{request.message}'")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
