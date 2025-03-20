import { Brightness7, DarkMode } from '@mui/icons-material';
import { Button, IconButton, Switch } from '@mui/material';
import axios from 'axios';


interface HeaderProps {
    theme: "light" | "dark";
    toggleTheme: () => void;
}

export default function Header({ theme, toggleTheme }: HeaderProps) {
  
    // Only show the logout button if we are not on the /login route.
    const showLogout = !window.location.href.includes('/#/login');
    console.log( window.location.href.includes('/#/login'))
    const handleLogout = async () => {
      await axios.post("/auth/cookie/logout");
      window.location.href = "/#/login"
      return;
    };
  
    return (
      <div className="theme-toggle">
        <IconButton onClick={toggleTheme} color="inherit">
          {theme === "light" ? <Brightness7 /> : <DarkMode />}
        </IconButton>
        <Switch checked={theme === "dark"} onChange={toggleTheme} />
        {showLogout && (
          <Button variant="outlined" onClick={handleLogout}>
            Logout
          </Button>
        )}
      </div>
    );
  }