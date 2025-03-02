import { useState } from 'react'
import './App.css'
import LoginForm from './components/LoginForm'
import { Switch, IconButton } from "@mui/material";
import { Brightness7, DarkMode } from "@mui/icons-material";

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  // Toggle theme function
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  return (
    <div className={`app ${theme}`}>
      {/* Theme Toggle in the Top Right Corner */}
      <div className="theme-toggle">
        <IconButton onClick={toggleTheme} color="inherit">
          {theme === "light" ? <Brightness7 /> : <DarkMode />}
        </IconButton>
        <Switch checked={theme === "dark"} onChange={toggleTheme} />
      </div>

      {/* Centered Login Form */}
      <div className="login-container">
        <LoginForm />
      </div>
    </div>
  )
}

export default App
