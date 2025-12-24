# Integrating Copilot Studio with a Power Apps Canvas App

This guide provides a step-by-step process for embedding a Microsoft Copilot Studio bot into a Power Apps Canvas App. This allows users to interact with your copilot directly within the app, creating a seamless and integrated experience.

## Prerequisites

1.  **A Published Copilot:** You must have a copilot created and published in Microsoft Copilot Studio.
2.  **A Canvas App:** You need an existing Canvas App (or create a new one) where you want to embed the copilot.
3.  **Correct Permissions:** You need maker permissions in both Power Apps and Copilot Studio in the same environment.

---

## Step 1: Get Your Copilot's Details

Before you can add the copilot to your Canvas App, you need two key pieces of information from Copilot Studio.

1.  Open your copilot in the [Copilot Studio portal](https://copilotstudio.microsoft.com/).
2.  In the left-hand navigation menu, go to **Settings** -> **Channels**.
3.  Select **Mobile app**. A pane will appear.
4.  Copy the **Bot ID** (also called "Schema Name") and the **Environment ID**. You will need these values to configure the component in your Canvas App. Keep them handy.

![Copilot Details Pane](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/media/chatbot-control/pva-details-pane-for-bot-id.png)
*(Image courtesy of Microsoft documentation)*

---

## Step 2: Add the Chatbot Component to Your Canvas App

1.  Open your Canvas App in the Power Apps Studio editor.
2.  From the app authoring menu, select the **Insert** pane.
3.  Expand the **Input** category.
4.  Select the **Chatbot (preview)** component to add it to a screen in your app.

This will place a control on your screen that will render the copilot.

---

## Step 3: Configure the Chatbot Component

With the Chatbot component selected on your screen, you need to connect it to your specific copilot.

1.  Go to the **Properties** pane on the right side of the editor.
2.  Select the **Advanced** tab.
3.  Find the following properties and paste the values you copied in Step 1:
    *   **`Bot schema name`**: Paste the **Bot ID** here.
    *   **`Environment ID`**: Paste the **Environment ID** here.

The component should now be linked to your copilot. You might see a "Getting ready" message, and then the copilot's welcome message should appear in the design canvas.

---

## Step 4: Handling User Authentication (Security)

To ensure the copilot honors the user's security role, it needs to know who the user is. The Chatbot component helps facilitate this.

1.  **Configure SSO in Copilot Studio:**
    *   In the Copilot Studio portal, go to **Settings** -> **Security**.
    *   Select **Authentication**.
    *   Choose the **"Only for Teams and Power Apps"** option. This is the simplest method and enables Single Sign-On (SSO) for apps in the same environment. For broader web apps, you would configure "Manual" authentication with Azure AD.
    *   When configured correctly, the copilot will automatically have access to the logged-in user's identity token from Power Apps.

2.  **How It Works:**
    *   When a user signs into the Canvas App, they are already authenticated with their Microsoft account.
    *   The Chatbot component automatically uses this identity.
    *   When the copilot performs an action that queries Dataverse (like "Show me my work orders"), it runs that query *as the logged-in user*.
    *   Dataverse then automatically filters the results based on that user's security roles and business unit, just as we designed. No extra token passing is required in the Canvas App for this scenario.

---

## Example Scenario

1.  A field technician opens their "Field Service Mobile" Canvas App.
2.  On the main screen, they see the embedded "Field Service Copilot".
3.  The technician types: `What are my priority tasks today?`
4.  The copilot, knowing the user is the authenticated technician, triggers a topic that queries Dataverse for `bookableresourcebooking` records.
5.  The query is automatically filtered to show only bookings where the technician is the assigned resource and the priority is high.
6.  The copilot displays a list of the high-priority bookings directly in the chat window inside the Canvas App.

By following these steps, you can successfully embed a secure, context-aware copilot directly into a Power Apps Canvas App, providing significant value to your users by bringing conversational AI into their daily workflow.
