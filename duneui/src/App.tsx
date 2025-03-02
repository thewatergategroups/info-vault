import { useState } from 'react'
import './App.css'
import LoginForm from './components/LoginForm'
import Chat from './components/Chat'
import { Switch, IconButton } from "@mui/material";
import { Brightness7, DarkMode } from "@mui/icons-material";

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  // Toggle theme function
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  return (
    <div className={`app ${theme}`}>
      {/* Theme Toggle in the Top Right Corner */}
      <div className="theme-toggle">
        <LoginForm />
        <IconButton onClick={toggleTheme} color="inherit">
          {theme === "light" ? <Brightness7 /> : <DarkMode />}
        </IconButton>
        <Switch checked={theme === "dark"} onChange={toggleTheme} />
      </div>

      <div className="login-container">
      <Chat />
      </div>
    </div>
  )
}

export default App
