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
import json

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

# --- Clients and Auth ---
openai.api_key = OPENAI_API_KEY
security = HTTPBearer()
AUTH_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
jwks = requests.get(JWKS_URI).json()
msal_app = msal.ConfidentialClientApplication(client_id=CLIENT_ID, authority=AUTH_AUTHORITY, client_credential=CLIENT_SECRET)

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # ... (omitted for brevity, same as before)
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

# --- Dataverse & LLM Functions ---
def get_fetchxml_from_llm(user_message: str) -> str:
    # ... (omitted for brevity, same as before)
    system_prompt = """
    You are an AI assistant that translates natural language questions into Microsoft Dataverse FetchXML queries.
    You must only respond with the FetchXML query, enclosed in a single ```xml ... ``` block. Do not provide any explanation.
    The user is asking questions related to Dynamics 365 Field Service.
    Key entities: 'workorder' (msdyn_workorder), 'account', 'bookableresourcebooking'.
    """
    try:
        completion = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}], temperature=0.0)
        response_text = completion.choices[0].message.content
        fetch_xml = response_text.split("```xml")[1].split("```")[0].strip()
        return fetch_xml
    except Exception as e:
        return f"<error>Could not generate FetchXML: {e}</error>"

def execute_fetchxml(fetch_xml: str, dataverse_token: str) -> dict:
    """Executes a FetchXML query against the Dataverse API."""
    headers = {
        "Authorization": f"Bearer {dataverse_token}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": "odata.include-annotations=\"*\"",
    }
    # The entity set name is the plural of the entity logical name
    entity_name = fetch_xml.split('<entity name="')[1].split('"')[0]
    entity_set = f"{entity_name}s" # Simple pluralization, may need adjustment
    
    api_url = f"{DATAVERSE_API_ENDPOINT}/api/data/v9.2/{entity_set}?fetchXml={requests.utils.quote(fetch_xml)}"
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error executing FetchXML: {response.text}")

def format_results(results: dict) -> str:
    """Formats the JSON results from Dataverse into a readable string."""
    if not results or not results.get("value"):
        return "I couldn't find any results for your query."
    
    records = results["value"]
    if len(records) == 1:
        record = records[0]
        formatted_record = "\n".join([f"- {key}: {value}" for key, value in record.items() if not key.startswith('@')])
        return f"I found one record:\n{formatted_record}"
    else:
        summary = f"I found {len(records)} records. Here are the first few:\n"
        for i, record in enumerate(records[:3]): # Show first 3
             summary += f"\nRecord {i+1}:\n" + "\n".join([f"- {key}: {value}" for key, value in record.items() if not key.startswith('@')])
        return summary

# --- API ---
class ChatRequest(BaseModel): message: str
class ChatResponse(BaseModel): reply: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token_data: dict = Depends(validate_token)):
    user_name = token_data["payload"].get("name", "Unknown User")
    
    obo_result = msal_app.acquire_token_on_behalf_of(user_assertion=token_data["raw_token"], scopes=[DATAVERSE_SCOPE])
    if "access_token" not in obo_result:
        raise HTTPException(status_code=500, detail="Failed to acquire downstream token.")
        
    dataverse_token = obo_result["access_token"]
    
    generated_fetchxml = get_fetchxml_from_llm(request.message)
    if generated_fetchxml.startswith("<error>"):
        return ChatResponse(reply=generated_fetchxml)
        
    query_results = execute_fetchxml(generated_fetchxml, dataverse_token)
    
    formatted_reply = format_results(query_results)
    
    return ChatResponse(reply=formatted_reply)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
