/**
 * Authentication helper utilities
 */
window.authHelpers = {
  getToken() {
    return localStorage.getItem("token") || localStorage.getItem("auth_token") || null;
  },
  getUser() {
    const u = localStorage.getItem("user") || localStorage.getItem("user_profile");
    try {
      return u ? JSON.parse(u) : null;
    } catch (e) {
      return null;
    }
  },
  isLoggedIn() {
    return !!this.getToken();
  }
};
