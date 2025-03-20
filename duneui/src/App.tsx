import { useState } from 'react'
import './App.css'
import LoginForm from './components/LoginForm'
import Home from './components/Home'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header'
function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  // Toggle theme function
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  return (
    <div className={`app ${theme}`}>
      {/* Theme Toggle in the Top Right Corner */}
      <Header theme={theme} toggleTheme={toggleTheme}/>
      <HashRouter>
        <Routes>
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="*" element={<Navigate to="/home" />} />
        </Routes>
      </HashRouter>
    </div>
  )
}

export default App
