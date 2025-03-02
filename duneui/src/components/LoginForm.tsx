import { Button } from "@mui/material";
import { Google } from "@mui/icons-material"; // Google icon from MUI

declare global {
  interface Window {
    google: any;
  }
}

export default function LoginForm() {
  const signInWithGoogle = () => {
    window.location.href = "/google/login";
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