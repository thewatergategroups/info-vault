import React from "react";
import { Brightness7, DarkMode } from "@mui/icons-material";
import { Button, IconButton, Switch, Box } from "@mui/material";
import axios from "axios";

interface HeaderProps {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

export default function Header({ theme, toggleTheme }: HeaderProps) {
  // Only show the logout button if we are not on the /login route.
  const showLogout = !window.location.href.includes("/#/login");

  const handleLogout = async () => {
    await axios.post("/auth/cookie/logout");
    window.location.href = "/#/login";
  };

  return (
    <Box
      className="theme-toggle"
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      {/* Left side: Navigation Links */}
      <Box>
        <Button color="inherit" href="#/chat">
          Chat
        </Button>
        <Button color="inherit" href="#/docs">
          Docs
        </Button>
      </Box>

      {/* Right side: Theme Toggle and Logout */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <IconButton onClick={toggleTheme} color="inherit">
          {theme === "light" ? <Brightness7 /> : <DarkMode />}
        </IconButton>
        <Switch checked={theme === "dark"} onChange={toggleTheme} />
        {showLogout && (
          <Button variant="outlined" onClick={handleLogout}>
            Logout
          </Button>
        )}
      </Box>
    </Box>
  );
}
