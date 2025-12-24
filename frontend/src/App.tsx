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
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    setIsLoading(true);
    setResponse("");

    try {
      const apiResponse = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          user_token: "placeholder-jwt-token", // Placeholder for now
        }),
      });

      if (!apiResponse.ok) {
        throw new Error(`HTTP error! status: ${apiResponse.status}`);
      }

      const data = await apiResponse.json();
      setResponse(data.reply);
    } catch (error) {
      console.error("Failed to send message:", error);
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
            <div
              style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
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
          </CardBody>
        </Card>
      </div>
    </FluentProvider>
  );
}

export default App;

