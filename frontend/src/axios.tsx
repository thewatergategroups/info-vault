import axios from "axios";

export async function checkUser() {
    try {
      const resp = await axios.get("/users/me");
      return resp.data
    } catch {
        return null
    }
  }

