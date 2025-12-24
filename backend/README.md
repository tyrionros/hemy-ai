# Backend: D365 Field Service Copilot

This directory contains the Python backend service for the Dynamics 365 Field Service Copilot. It is built using FastAPI.

## 1. Project Setup

These steps guide you through setting up the local development environment for the backend service.

### Prerequisites

*   Python 3.9+
*   `pip` and `venv`

### Instructions

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a Python virtual environment:**
    This isolates the project's dependencies from your system's Python installation.
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    Your shell prompt should now be prefixed with `(.venv)`.

4.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```
    fastapi
    uvicorn[standard]
    python-dotenv
    requests
    ```
    Then, install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

## 2. Running the Development Server

1.  **Create the main application file:**
    Create a file named `main.py` and add the following "Hello World" code to verify the setup:

    ```python
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"message": "D365 Field Service Copilot backend is running."}

    if __name__ == "__main__":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    ```

2.  **Start the server:**
    Run the following command in your terminal (with the virtual environment activated):
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **Verify:**
    Open your web browser and navigate to `http://localhost:8000`. You should see the JSON response: `{"message":"D365 Field Service Copilot backend is running."}`.

## 3. Environment Variables

For connecting to Dataverse and other services, we will use a `.env` file. Create a `.env` file in the `backend` directory. It will store sensitive information like API keys and endpoints.

**Example `.env` file:**
```
AZURE_TENANT_ID="your-tenant-id"
AZURE_CLIENT_ID="your-client-id"
AZURE_CLIENT_SECRET="your-client-secret"
DATAVERSE_API_ENDPOINT="https://your-org.api.crm.dynamics.com/api/data/v9.2"
```

**Note:** Never commit the `.env` file to version control. Add `.venv` and `.env` to the project's `.gitignore` file.
