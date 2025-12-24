# Integrating Copilot Studio with Power Pages

This guide explains how to add a Microsoft Copilot Studio bot to a Power Pages site. This enables you to provide a rich, conversational experience for your site visitors, whether they are anonymous guests or authenticated users.

## Prerequisites

1.  **A Published Copilot:** You must have a copilot created and published in Microsoft Copilot Studio.
2.  **A Power Pages Site:** You need an existing Power Pages site (or create a new one).
3.  **Correct Permissions:** You need maker permissions for both Power Pages and Copilot Studio in the same environment.

---

## Step-by-Step Integration Guide

Adding a copilot to a Power Pages site is a straightforward process within the Power Pages design studio.

1.  **Open the Power Pages Design Studio:**
    *   Navigate to the [Power Pages portal](https://make.powerpages.microsoft.com/) and select **Edit** on the site you want to modify.

2.  **Navigate to the Target Page:**
    *   In the design studio, go to the page where you want the chatbot to appear. This is often the home page, but it can be any page on your site.

3.  **Add the Chatbot Component:**
    *   On the left-hand component panel, click the **"+"** icon to add a new component.
    *   Select the **Chatbot** component from the list.

    ![Add Chatbot Component in Power Pages](https://learn.microsoft.com/en-us/power-pages/getting-started/media/add-chatbot.png)
    *(Image courtesy of Microsoft documentation)*

4.  **Configure the Chatbot:**
    *   A dialog window titled "Add a chatbot" will appear.
    *   **Select a bot:** Choose your desired copilot from the dropdown menu. This list is automatically populated with the copilots available in your environment.
    *   **Requires user to sign in:** This is a critical setting that determines the copilot's behavior and security context.

---

## Understanding Authentication Scenarios

The "Requires user to sign in" toggle fundamentally changes how your copilot operates.

### Scenario A: Public-Facing Copilot (Sign-in NOT Required)

If you **turn off** the "Requires user to sign in" toggle:

*   **Behavior:** The chatbot will be visible and usable by **all visitors** to your Power Pages site, including anonymous guests.
*   **Security Context:** The copilot runs without a specific user context. It cannot access any data from Dataverse that is protected by user-level security roles.
*   **Use Cases:** This is ideal for public-facing websites where the copilot acts as a general guide, answers frequently asked questions (FAQs), or captures basic information like sales leads.

**Example:** An anonymous visitor asks, "What services do you offer?" The copilot provides a pre-programmed list of services.

### Scenario B: Authenticated User Copilot (Sign-in IS Required)

If you **turn on** the "Requires user to sign in" toggle:

*   **Behavior:** The chatbot component will only be fully functional for users who have signed into the Power Pages site. Your site must have an identity provider configured (e.g., Azure AD, Azure AD B2C, or other OAuth providers). If a user is not signed in, the chatbot will prompt them to do so before they can begin a conversation.
*   **Security Context:** The copilot automatically operates **in the context of the logged-in user**. This is the key to providing personalized and secure data.
*   **How it Works:** When an authenticated user interacts with the copilot, any Dataverse queries performed by the copilot are automatically filtered by that user's security roles, business unit, and table permissions. You do not need to manage tokens manually.
*   **Use Cases:** This is perfect for customer portals, partner sites, or internal employee sites where users need to access their own specific information securely.

**Example:** A logged-in customer asks, "What is the status of my latest support ticket?" The copilot queries the `case` table in Dataverse and, because it's running as that specific user, only finds and displays the tickets linked to that customer's account.

---

## Finalizing and Styling

*   After configuring, close the dialog. The chatbot component will appear on your page, typically as a floating icon in the bottom-right corner.
*   You can further customize the look and feel of the chatbot component (e.g., its color and position) using the styling options in the Power Pages design studio.
*   **Preview and Sync** your site to see the chatbot in action.

By leveraging this native integration, you can quickly deploy a powerful and secure conversational AI on your Power Pages site for both public and private audiences.
