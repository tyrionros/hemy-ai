from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
import requests
import msal

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="D365 Field Service Copilot Backend",
    description="API for the Dynamics 365 Field Service Copilot.",
    version="0.1.0"
)

# --- Environment Variables ---
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
DATAVERSE_SCOPE = os.getenv("DATAVERSE_SCOPE") 
DATAVERSE_API_ENDPOINT = os.getenv("DATAVERSE_API_ENDPOINT") # e.g., "https://your-org.api.crm.dynamics.com"

# --- Authentication ---
security = HTTPBearer()
AUTH_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

jwks = requests.get(JWKS_URI).json()

msal_app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTH_AUTHORITY,
    client_credential=CLIENT_SECRET,
)

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {key: value for key, value in jwks["keys"][0].items() if key in ["kty", "kid", "use", "n", "e"]}
        
        if rsa_key:
            decoded_token = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=CLIENT_ID, issuer=f"{AUTH_AUTHORITY}/v2.0")
            return {"payload": decoded_token, "raw_token": token}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find appropriate key.")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {e}")

# --- API Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "D365 Field Service Copilot backend is running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token_data: dict = Depends(validate_token)):
    user_name = token_data["payload"].get("name", "Unknown User")
    
    obo_result = msal_app.acquire_token_on_behalf_of(user_assertion=token_data["raw_token"], scopes=[DATAVERSE_SCOPE])

    if "access_token" in obo_result:
        dataverse_token = obo_result["headers"]["Authorization"] = f"Bearer {obo_result['access_token']}"
        
        # Call Dataverse WhoAmI function
        whoami_url = f"{DATAVERSE_API_ENDPOINT}/api/data/v9.2/WhoAmI"
        headers = {"Authorization": dataverse_token}
        response = requests.get(whoami_url, headers=headers)

        if response.status_code == 200:
            user_id = response.json()["UserId"]
            return ChatResponse(reply=f"Hello, {user_name}! Your Dataverse User ID is: {user_id}. You said: '{request.message}'")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error calling Dataverse: {response.text}")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to acquire downstream token.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
