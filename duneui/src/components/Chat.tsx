import React, { useEffect, useState } from "react";
import {
  Box,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  TextField,
  SelectChangeEvent,
} from "@mui/material";
import axios from "axios";

interface Session {
  session_id: string;
}

interface Message {
  role: "user" | "assistant" | string; // fallback if role is unknown
  content: string;
}

interface ChatProps {
  theme: "light" | "dark";
}

export const ChatPage: React.FC<ChatProps> = ({ theme }) => {
  // Session state
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<string>("");

  // Chat history state
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [streamingOutput, setStreamingOutput] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  // Loading state for sessions
  const [sessionsLoading, setSessionsLoading] = useState<boolean>(false);

  // Input message state
  const [inputMessage, setInputMessage] = useState<string>("");

  // Provider state ("openai" or "ollama")
  const [selectedProvider, setSelectedProvider] = useState<"openai" | "ollama">(
    "ollama"
  );

  useEffect(() => {
    fetchSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchSessions = async () => {
    setSessionsLoading(true);
    try {
      const response = await axios.get<Session[]>("/chat/sessions");
      setSessions(response.data);
      if (response.data.length > 0 && !selectedSession) {
        const firstSession = response.data[0].session_id;
        setSelectedSession(firstSession);
        fetchChatHistory(firstSession);
      }
    } catch (error) {
      console.error("Error fetching sessions", error);
    } finally {
      setSessionsLoading(false);
    }
  };

  const fetchChatHistory = async (session_id: string) => {
    try {
      const response = await axios.get<Message[]>("/chat/history", {
        params: { session_id },
      });
      setChatHistory(response.data);
    } catch (error) {
      console.error("Error fetching chat history", error);
    }
  };

  const handleSessionChange = (e: SelectChangeEvent) => {
    const sessionId = e.target.value as string;
    setSelectedSession(sessionId);
    fetchChatHistory(sessionId);
  };

  const handleNewSession = async () => {
    try {
      const response = await axios.get<{ session_id: string }>("/chat/session");
      const newSessionId = response.data.session_id;
      setSelectedSession(newSessionId);
      fetchSessions(); // refresh sessions list
      setChatHistory([]); // clear chat history
    } catch (error) {
      console.error("Error creating new session", error);
    }
  };

  const handleDeleteSession = async () => {
    if (!selectedSession) return;
    try {
      await axios.delete("/chat/session", { params: { session_id: selectedSession } });
      setChatHistory([]);
      setSelectedSession("");
      fetchSessions();
    } catch (error) {
      console.error("Error deleting session", error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedSession) return;
    const userMessage: Message = { role: "user", content: inputMessage };
    setChatHistory((prev) => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");

    setStreamingOutput("");
    setIsStreaming(true);

    const payload = {
      message: messageToSend,
      session_id: selectedSession,
      provider: selectedProvider,
    };

    try {
      const response = await fetch("/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.body) throw new Error("No response body from stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;
      let assistantResponse = "";
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunk = decoder.decode(value || new Uint8Array(), { stream: !done });
        assistantResponse += chunk;
        setStreamingOutput(assistantResponse);
      }
      const newAssistantMessage: Message = { role: "assistant", content: assistantResponse };
      setChatHistory((prev) => [...prev, newAssistantMessage]);
    } catch (error) {
      console.error("Error streaming message", error);
    } finally {
      setIsStreaming(false);
      setStreamingOutput("");
    }
  };

  // Override colours based on the theme prop
  const textColor = theme === "dark" ? "#ffffff" : "#000000";
  const paperBackground = theme === "dark" ? "#333333" : "#f5f5f5";
  const dividerColor = theme === "dark" ? "#555" : "#ccc";

  return (
    <Box
      className='chat-input'
      sx={{
        width: "100%",
        height: "620px", // Finite fixed height
        display: "flex",
        flexDirection: "column",

      }}
    >
      {/* Session Controls */}
      <Paper
        sx={{
          p: 2,
          display: "flex",
          flexWrap: "nowrap",
          alignItems: "center",
          gap: 2,
          backgroundColor: paperBackground,
          color: textColor,
        }}
      >
        {sessionsLoading ? (
          <CircularProgress size={24} />
        ) : (
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel id="session-select-label" sx={{ color: textColor }}>
              Session
            </InputLabel>
            <Select
              labelId="session-select-label"
              value={selectedSession}
              label="Session"
              onChange={handleSessionChange}
              sx={{ color: textColor, borderColor: textColor }}
            >
              {sessions.map((session) => (
                <MenuItem key={session.session_id} value={session.session_id}>
                  {session.session_id}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <Button variant="contained" onClick={handleNewSession}>
          New Session
        </Button>
        <Button
          variant="outlined"
          onClick={handleDeleteSession}
          disabled={!selectedSession}
        >
          Delete Session
        </Button>

        {/* Provider Dropdown */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel id="provider-select-label" sx={{ color: textColor }}>
            Provider
          </InputLabel>
          <Select
            labelId="provider-select-label"
            value={selectedProvider}
            label="Provider"
            onChange={(e) =>
              setSelectedProvider(e.target.value as "openai" | "ollama")
            }
            sx={{ color: textColor }}
          >
            <MenuItem value="ollama">Ollama</MenuItem>
            <MenuItem value="openai">OpenAI</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Chat Area */}
      <Paper
        sx={{
          flexGrow: 1,
          width: "100%",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          backgroundColor: paperBackground,
          color: textColor,
        }}
      >
        {/* Chat History Container */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: "auto",
            p: 2,
            backgroundColor: paperBackground,
            color: textColor,
          }}
        >
          {chatHistory.map((msg, idx) => {
            const isUser = msg.role === "user";
            return (
              <Box
                key={idx}
                sx={(theme) => ({
                  alignSelf: isUser ? "flex-end" : "flex-start",
                  maxWidth: "70%",
                  mb: 1,
                  p: 1,
                  borderRadius: theme.shape.borderRadius,
                  backgroundColor: isUser
                    ? theme.palette.primary.main
                    : theme.palette.secondary.main,
                  color: isUser
                    ? theme.palette.getContrastText(theme.palette.primary.main)
                    : theme.palette.getContrastText(theme.palette.secondary.main),
                  whiteSpace: "pre-line",
                })}
              >
                {msg.content}
              </Box>
            );
          })}
          {isStreaming && (
            <Box
              sx={(theme) => ({
                alignSelf: "flex-start",
                maxWidth: "70%",
                mb: 1,
                p: 1,
                borderRadius: theme.shape.borderRadius,
                backgroundColor: theme.palette.secondary.main,
                color: theme.palette.getContrastText(theme.palette.secondary.main),
                whiteSpace: "pre-line",
              })}
            >
              {streamingOutput}
            </Box>
          )}
        </Box>

        {/* Input Area */}
        <Box
          sx={{
            p: 2,
            display: "flex",
            gap: 1,
            borderTop: `1px solid ${dividerColor}`,
            backgroundColor: paperBackground,
            color: textColor,
          }}
        >
          <TextField
            fullWidth
            label="Type your message"
            variant="outlined"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            sx={{
              "& .MuiInputLabel-root": { color: textColor },
              "& .MuiOutlinedInput-root": {
                "& fieldset": { borderColor: dividerColor },
                "&:hover fieldset": { borderColor: dividerColor },
                "&.Mui-focused fieldset": { borderColor: dividerColor },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={isStreaming || !selectedSession}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatPage;
