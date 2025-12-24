# Frontend: D365 Field Service Copilot

This directory contains the React frontend for the Dynamics 365 Field Service Copilot. It is built using React, TypeScript, and Vite, and is designed to be embedded as a Model-Driven App Custom Page in Dynamics 365.

## 1. Project Setup

These steps guide you through setting up the local development environment for the frontend application.

### Prerequisites

*   Node.js (LTS version recommended)
*   `npm` (comes with Node.js) or `yarn`

### Instructions

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Initialize the React project using Vite:**
    If you are starting from scratch, run the following command and follow the prompts to create a new project with the `react-ts` template.
    ```bash
    # If you use npm
    npm create vite@latest . -- --template react-ts

    # If you use yarn
    yarn create vite . --template react-ts
    ```
    *Note: The `.` in the command creates the project in the current `frontend` directory.*

3.  **Install dependencies:**
    After the project is created, install the initial dependencies.
    ```bash
    # If you use npm
    npm install

    # If you use yarn
    yarn
    ```

4.  **Install additional libraries:**
    We will use Microsoft's Fluent UI for a native look and feel, and MSAL for authentication.
    ```bash
    # If you use npm
    npm install @fluentui/react-components @azure/msal-browser @azure/msal-react

    # If you use yarn
    yarn add @fluentui/react-components @azure/msal-browser @azure/msal-react
    ```

## 2. Running the Development Server

1.  **Start the development server:**
    Run the following command in your terminal:
    ```bash
    # If you use npm
    npm run dev

    # If you use yarn
    yarn dev
    ```

2.  **Verify:**
    Vite will output a local URL (usually `http://localhost:5173`). Open it in your browser to see the default React application.

## 3. Integrating with Dynamics 365

This application is intended to be run as a Custom Page inside a Model-Driven App.

1.  **Build for Production:**
    When ready to deploy, you will need to build the static assets.
    ```bash
    # If you use npm
    npm run build

    # If you use yarn
    yarn build
    ```
    This command creates a `dist` directory containing the compiled HTML, CSS, and JavaScript files.

2.  **Create a Web Resource:**
    The contents of the `dist` directory will be uploaded as Web Resources into your Dynamics 365 solution. The primary file will be the `index.html` file.

3.  **Configure the Custom Page:**
    In your solution, create a new Custom Page and point it to the `index.html` Web Resource. This Custom Page can then be added to the navigation of your Field Service Model-Driven App.