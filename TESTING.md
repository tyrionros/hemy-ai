# Testing the Application

To test the initial integration between the frontend and backend, you need to run both development servers simultaneously in two separate terminals.

## Terminal 1: Run the Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Activate your Python virtual environment:**
    *   macOS/Linux: `source .venv/bin/activate`
    *   Windows: `.venv\Scripts\activate`

3.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The backend will be running at `http://localhost:8000`.

## Terminal 2: Run the Frontend

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Start the Vite development server:**
    ```bash
    # Using npm
    npm run dev

    # Using yarn
    yarn dev
    ```
    The frontend will be running at `http://localhost:5173` (or a similar port if 5173 is in use).

## Verification

1.  Open your web browser and navigate to the frontend URL (e.g., `http://localhost:5173`).
2.  You should see the "D365 Field Service Copilot" chat interface.
3.  Type a message in the input box and click "Send".
4.  The frontend will send a request to the backend. You should see a response in the UI like: `"You said: 'your message here'"`.
5.  In the backend terminal, you will see a log message showing the placeholder token being received.
