import { Configuration } from "@azure/msal-browser";

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: "YOUR_CLIENT_ID_HERE", // Replace with your Azure AD application's Client ID
    authority: "https://login.microsoftonline.com/YOUR_TENANT_ID_HERE", // Replace with your Tenant ID
    redirectUri: "/", // Must be configured as a redirect URI in your Azure AD app registration
  },
  cache: {
    cacheLocation: "sessionStorage", // This configures where your cache will be stored
    storeAuthStateInCookie: false, // Set this to "true" if you are having issues on IE11 or Edge
  },
};

// Add scopes here for ID token to be used at Microsoft identity platform endpoints.
export const loginRequest = {
  scopes: ["User.Read"],
};

// Add scopes here for the access token to be used to call the backend API.
export const tokenRequest = {
  scopes: ["api://YOUR_BACKEND_API_CLIENT_ID_HERE/user_impersonation"], // Replace with your backend API's scope
};
