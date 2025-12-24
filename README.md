# Hemy-AI: D365 Field Service Copilot

This repository contains the source code for a security-aware AI Copilot for Dynamics 365 Field Service.

## Project Structure

The project is organized into two main components: a backend service and a frontend application.

### `/backend`

This directory contains the Python **FastAPI** backend service. Its responsibilities include:

*   Providing a secure API endpoint for the frontend.
*   Handling user authentication via the On-Behalf-Of (OBO) flow.
*   Translating natural language queries into Dataverse API calls using an LLM.
*   Executing queries against Dataverse while impersonating the user to enforce security roles.

For detailed setup instructions, see the `backend/README.md` file.

### `/frontend`

This directory contains the **React + TypeScript** frontend application, built with Vite. Its responsibilities include:

*   Providing a clean, modern chat interface for the user.
*   Authenticating the user within the Dynamics 365 context.
*   Sending user queries to the backend and displaying the results.
*   Rendering actionable buttons based on the copilot's response.

This application is designed to be deployed as a **Model-Driven App Custom Page** inside Dynamics 365.

For detailed setup instructions, see the `frontend/README.md` file.

