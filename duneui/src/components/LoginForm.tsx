
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
      <button className="button" onClick={signInWithGoogle}>
        Sign in with Google
      </button>
    );
  }
