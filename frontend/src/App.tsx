import { ReactNode, useEffect, useState } from 'react'
import './App.css'
import LoginForm from './components/LoginForm'
import DocumentsPage from './components/Documents'
import Chat from './components/Chat'
import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Header from './components/Header'
import { AuthProvider,useAuth } from './auth'
import { checkUser } from './axios'


interface ProtectedRouteProps {
  children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user,login,logout } = useAuth();
  const location = useLocation();
  
  useEffect(()=>{
    handleLoggedInCheck()
  },[])

  const handleLoggedInCheck = async () => {
      const user = await checkUser();
      if (user !== null) {
        login(user)
        return
      }
      logout()
    }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  // Toggle theme function
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  return (
    <AuthProvider>
    <div className={`app ${theme}`}>
      {/* Theme Toggle in the Top Right Corner */}
      <Header theme={theme} toggleTheme={toggleTheme}/>
      <HashRouter>
        <Routes>
          <Route path="/chat" element={
            <ProtectedRoute>
              <Chat theme={theme} />
            </ProtectedRoute>
            } />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/docs" element={
            <ProtectedRoute>
              <DocumentsPage  theme={theme}/>
            </ProtectedRoute>
            } />
          <Route path="*" element={<Navigate to="/chat" />} />
        </Routes>
      </HashRouter>
    </div>
    </AuthProvider>
  )
}

export default App
