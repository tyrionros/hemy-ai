import { useState } from "react";
import {
  FluentProvider,
  webLightTheme,
  Input,
  Button,
  Spinner,
  Body1,
  Title3,
  Card,
  CardHeader,
  CardBody,
} from "@fluentui/react-components";
import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
  useMsal,
  useIsAuthenticated,
} from "@azure/msal-react";
import { loginRequest, tokenRequest } from "./authConfig";
import "./App.css";

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch((e) => {
      console.error(e);
    });
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !isAuthenticated) return;

    setIsLoading(true);
    setResponse("");

    const request = {
      ...tokenRequest,
      account: accounts[0],
    };

    try {
      const tokenResponse = await instance.acquireTokenSilent(request);
      const userToken = tokenResponse.accessToken;

      const apiResponse = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${userToken}`, // Pass token in header
        },
        body: JSON.stringify({
          message: message,
          user_token: userToken, // Also in body as per original plan
        }),
      });

      if (!apiResponse.ok) {
        throw new Error(`HTTP error! status: ${apiResponse.status}`);
      }

      const data = await apiResponse.json();
      setResponse(data.reply);
    } catch (error) {
      console.error("Failed to send message:", error);
      if (error instanceof Error && error.name === "InteractionRequiredAuthError") {
        instance.acquireTokenPopup(request);
      }
      setResponse("Failed to get a response from the server.");
    } finally {
      setIsLoading(false);
      setMessage("");
    }
  };

  return (
    <FluentProvider theme={webLightTheme}>
      <div className="app-container">
        <Card style={{ width: "600px" }}>
          <CardHeader>
            <Title3>D365 Field Service Copilot</Title3>
          </CardHeader>
          <CardBody>
            <AuthenticatedTemplate>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                <Input
                  value={message}
                  onChange={(_, data) => setMessage(data.value)}
                  placeholder="Ask something about your work orders..."
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  disabled={isLoading}
                />
                <Button
                  appearance="primary"
                  onClick={handleSendMessage}
                  disabled={isLoading}
                >
                  Send
                </Button>

                {isLoading && <Spinner label="Thinking..." />}

                {response && (
                  <Card>
                    <CardBody>
                      <Body1>{response}</Body1>
                    </CardBody>
                  </Card>
                )}
              </div>
            </AuthenticatedTemplate>
            <UnauthenticatedTemplate>
              <Body1>Please sign in to use the Copilot.</Body1>
              <Button appearance="primary" onClick={handleLogin}>
                Sign In
              </Button>
            </UnauthenticatedTemplate>
          </CardBody>
        </Card>
      </div>
    </FluentProvider>
  );
}

export default App;
