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

# --- Authentication ---
security = HTTPBearer()
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
DATAVERSE_SCOPE = os.getenv("DATAVERSE_SCOPE") # e.g., "https://your-org.api.crm.dynamics.com/.default"

AUTH_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

jwks = requests.get(JWKS_URI).json()

# MSAL Confidential Client for OBO flow
msal_app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTH_AUTHORITY,
    client_credential=CLIENT_SECRET,
)

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate the bearer token and return the decoded payload and the raw token."""
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = { "kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"] }
        
        if rsa_key:
            decoded_token = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                issuer=f"{AUTH_AUTHORITY}/v2.0"
            )
            # Return both the decoded token and the original token for OBO flow
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
    """A simple endpoint to verify that the service is running."""
    return {"message": "D365 Field Service Copilot backend is running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token_data: dict = Depends(validate_token)):
    """
    The main endpoint for handling chat messages from the user.
    Requires a valid JWT, performs OBO flow, and gets a token for Dataverse.
    """
    user_name = token_data["payload"].get("name", "Unknown User")
    print(f"Request from authenticated user: {user_name}")

    # --- On-Behalf-Of Flow ---
    obo_result = msal_app.acquire_token_on_behalf_of(
        user_assertion=token_data["raw_token"],
        scopes=[DATAVERSE_SCOPE]
    )

    if "access_token" in obo_result:
        dataverse_token = obo_result["access_token"]
        print(f"Successfully acquired Dataverse token for {user_name}: {dataverse_token[:30]}...")

        # NEXT STEP: Use this `dataverse_token` to make secure API calls to Dataverse.
        # For example:
        # headers = {"Authorization": f"Bearer {dataverse_token}"}
        # response = requests.get("https://your-org.api.crm.dynamics.com/api/data/v9.2/whoami", headers=headers)
        # print(response.json())

        return ChatResponse(reply=f"{user_name}, you said: '{request.message}'. The OBO flow was successful.")
    else:
        print("OBO flow failed:", obo_result.get("error_description"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to acquire downstream token.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
