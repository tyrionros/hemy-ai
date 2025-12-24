from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
import requests
import msal
import openai

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
DATAVERSE_API_ENDPOINT = os.getenv("DATAVERSE_API_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# --- OpenAI Client ---
openai.api_key = OPENAI_API_KEY

# --- Authentication (existing code) ---
# ... (validate_token and msal_app setup remains the same)
security = HTTPBearer()
AUTH_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
jwks = requests.get(JWKS_URI).json()
msal_app = msal.ConfidentialClientApplication(client_id=CLIENT_ID, authority=AUTH_AUTHORITY, client_credential=CLIENT_SECRET)
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

# --- LLM Integration ---
def get_fetchxml_from_llm(user_message: str) -> str:
    """
    Uses an LLM to convert a natural language query into a Dataverse FetchXML query.
    """
    system_prompt = """
    You are an AI assistant that translates natural language questions into Microsoft Dataverse FetchXML queries.
    You must only respond with the FetchXML query, enclosed in a single ```xml ... ``` block. Do not provide any explanation.
    
    The user is asking questions related to Dynamics 365 Field Service.
    Here are some key entities and attributes:
    - Entity: 'workorder' (msdyn_workorder)
      - Attributes: 'msdyn_name', 'msdyn_workordertype', 'msdyn_systemstatus', 'msdyn_priority'
    - Entity: 'account'
      - Attributes: 'name', 'address1_city', 'address1_stateorprovince'
    - Entity: 'bookableresourcebooking' (Booking)
      - Attributes: 'starttime', 'endtime', 'bookingstatus'
      
    Example:
    User: "Show me all my active work orders in Seattle"
    AI:
    ```xml
    <fetch>
      <entity name="msdyn_workorder">
        <attribute name="msdyn_name" />
        <attribute name="msdyn_systemstatus" />
        <filter type="and">
          <condition attribute="msdyn_systemstatus" operator="eq" value="690970002" /> <!-- Active -->
          <link-entity name="account" from="accountid" to="msdyn_serviceaccount">
            <filter>
              <condition attribute="address1_city" operator="eq" value="Seattle" />
            </filter>
          </link-entity>
        </filter>
      </entity>
    </fetch>
    ```
    """
    
    try:
        completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0
        )
        response_text = completion.choices[0].message.content
        # Extract content from the xml block
        fetch_xml = response_text.split("```xml")[1].split("```")[0].strip()
        return fetch_xml
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"<error>Could not generate FetchXML: {e}</error>"

# --- API Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# --- Endpoints ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token_data: dict = Depends(validate_token)):
    user_name = token_data["payload"].get("name", "Unknown User")
    print(f"Request from authenticated user: {user_name}")

    # --- OBO Flow (to ensure we CAN get a token, though we don't use it in this step) ---
    obo_result = msal_app.acquire_token_on_behalf_of(user_assertion=token_data["raw_token"], scopes=[DATAVERSE_SCOPE])
    if "access_token" not in obo_result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to acquire downstream token.")
    
    # --- LLM generates FetchXML ---
    generated_fetchxml = get_fetchxml_from_llm(request.message)
    
    # For now, we return the generated XML to the user for verification.
    # The next step will be to execute this query.
    reply_message = f"Hello, {user_name}! I've translated your request into the following FetchXML query:\n\n{generated_fetchxml}"
    
    return ChatResponse(reply=reply_message)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
