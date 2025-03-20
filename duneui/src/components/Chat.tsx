import { useState, useRef, useEffect } from "react";
import {
  Button,
  Box,
  Typography,
  Collapse,
  IconButton,
  InputBase,
  Paper,
  useTheme,
} from "@mui/material";
import {  ExpandMore } from "@mui/icons-material";
import axios from "axios";

interface Message {
  role: "user" | "bot";
  content: string;
  thinking?: string;
}



export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [session_id, setSessionId] = useState('');
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  const [expanded, setExpanded] = useState<{ [key: number]: boolean }>({});
 
  async function getSession(){
    const response1 = await axios.get("/chat/sessions", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    setSessionId(response1.data[0].session_id)
  }
  
  useEffect(() => {
          getSession();
        }, []);
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      

      const response = await fetch("/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, provider: 'ollama',session_id: session_id }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botMessage = "";
      let thinkingMessage = "";
      let isThinking = false;

      setMessages((prev) => [...prev, { role: "bot", content: "", thinking: "" }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        for (let i = 0; i < chunk.length; i++) {
          if (chunk.substring(i, i + 7) === "<think>") {
            isThinking = true;
            i += 6;
            continue;
          }
          if (chunk.substring(i, i + 8) === "</think>") {
            isThinking = false;
            i += 7;
            continue;
          }
          if (isThinking) {
            thinkingMessage += chunk[i];
          } else {
            botMessage += chunk[i];
          }
        }

        setMessages((prev) =>
          prev.map((msg, i) =>
            msg.role === "bot" && i === prev.length - 1
              ? { ...msg, content: botMessage, thinking: thinkingMessage }
              : msg
          )
        );
      }

      setLoading(false);
    } catch (error) {
      console.error("Error streaming chat response:", error);
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !loading) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box
      sx={{
        maxWidth: "48rem",
        minWidth: "48rem",
        margin: "auto",
        padding: 2,
        height: "90%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        borderRadius: "10px",
      }}
    >
      {/* Message List */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          mb: 2,
          overflowY: "auto",
          scrollbarWidth: "none",
          "&::-webkit-scrollbar": { display: "none" },
        }}
      >
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              width: "90%",
            }}
          >
            {/* Thinking Dropdown Above Message with Collapse Button on Top */}
            {msg.thinking && (
              <Box
                sx={{
                  position: "relative",
                  width: "103%",
                }}
              >
                {/* Expand/Collapse Button at the Top */}
                <IconButton
                  onClick={() => setExpanded((prev) => ({ ...prev, [index]: !prev[index] }))}
                  size="small"
                  sx={{
                    position: "absolute",
                    left: "96%",
                    color: theme.palette.text.secondary,
                    boxShadow: theme.shadows[1],
                    zIndex: 10,
                  }}
                >
                  <ExpandMore
                    sx={{
                      fontSize: "18px",
                      transform: expanded[index] ? "rotate(180deg)" : "rotate(0deg)",
                      transition: "0.2s",
                    }}
                  />
                </IconButton>

                {/* Thinking Message Box */}
                <Collapse in={expanded[index]} timeout="auto">
                  <Box
                    sx={{
                      padding: 1,
                      borderRadius: "6px",
                      marginBottom: "8px",
                      backgroundColor: isDarkMode ? theme.palette.grey[700] : theme.palette.grey[300],
                    }}
                  >
                    <Typography variant="body2" sx={{ fontStyle: "italic", color: isDarkMode ? "#fff" : "#000" }}>
                      {msg.thinking}
                    </Typography>
                  </Box>
                </Collapse>
              </Box>
            )}

            {/* Bot Messages: Light Background */}
            {msg.role === "bot" && (
              <Box
                sx={{
                  width: "100%",
                  backgroundColor: isDarkMode ? theme.palette.grey[800] : theme.palette.grey[200],
                  padding: "10px",
                  borderRadius: "8px",
                  color: isDarkMode ? "#fff" : "#000",
                }}
              >
                <Typography>{msg.content}</Typography>
              </Box>
            )}

            {/* User Messages: Darker Grey Bubble */}
            {msg.role === "user" && (
              <Box
                sx={{
                  backgroundColor: "#666666",
                  padding: "10px",
                  borderRadius: "12px",
                  maxWidth: "80%",
                  color: "#fff",
                }}
              >
                <Typography>{msg.content}</Typography>
              </Box>
            )}
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Box - Darker in Dark Mode & Themed */}
      <Paper
        sx={{
          display: "flex",
          alignItems: "center",
          padding: "8px 12px",
          backgroundColor: isDarkMode ? theme.palette.grey[900] : theme.palette.background.paper,
          borderRadius: "24px",
          boxShadow: "none",
          border: `1px solid ${theme.palette.divider}`,
          width: "100%",
        }}
      >
        <InputBase
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type a message..."
          sx={{
            flex: 1,
            fontSize: "14px",
            padding: "6px",
            color: isDarkMode ? "#fff" : "#000",
          }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={sendMessage}
          disabled={loading}
          sx={{
            minWidth: "40px",
            padding: "6px 12px",
            borderRadius: "20px",
            fontSize: "12px",
            textTransform: "none",
          }}
        >
          Send
        </Button>
      </Paper>
    </Box>
  );
}