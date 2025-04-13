import { Button } from "@mui/material";
import { Google } from "@mui/icons-material";
import axios from "axios";
import { useEffect } from "react";
import { checkUser } from "../axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function LoginForm() {
  const {login} = useAuth()
  const navigate = useNavigate()
  
  const handleLoggedInCheck = async () => {
    const user = await checkUser();
    if (user !== null) {
      login(user)
      navigate("/chat")
    }
  }

  useEffect(() => {
    handleLoggedInCheck()   
      }, []);

  const signInWithGoogle = async () => {
    try {
      const { data } = await axios.get("/auth/cookie/google/authorize");
      if (data.authorization_url) {
        console.log(`navigating to ${data.authorization_url}`)
        window.location.href = data.authorization_url;
      } else {
        console.error("Authorization URL missing in response:", data);
      }
    } catch (error) {
      console.error("Error signing in with Google:", error);
    }
  };
  

  return (
    <Button
      variant="contained"
      color="secondary"
      startIcon={<Google />}
      onClick={signInWithGoogle}
      sx={{
        textTransform: "none", // Prevents all-uppercase text
        borderRadius: "8px",
        backgroundColor: "#4285F4", // Google Blue
        "&:hover": { backgroundColor: "#357ae8" },
      }}
    >
      Sign in with Google
    </Button>
  );
}
