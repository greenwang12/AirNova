export const ADMIN_TOKEN_KEY = "admin_token";

export const saveToken = (token: string) =>
  localStorage.setItem(ADMIN_TOKEN_KEY, token);

export const getToken = () => localStorage.getItem(ADMIN_TOKEN_KEY);

export const logout = () => localStorage.removeItem(ADMIN_TOKEN_KEY);
