import axios from "axios";

export async function checkUser(loginPage:boolean = false) {
    try {
      await axios.get("/users/me");
      if (loginPage){
        window.location.href = "/#/home";
      }
    } catch (error: any) {
      window.location.href = "/#/login";
    }
  }

