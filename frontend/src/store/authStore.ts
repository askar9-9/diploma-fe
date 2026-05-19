export const authStore = {
  getToken: () => localStorage.getItem('token'),
  setToken: (token: string) => localStorage.setItem('token', token),
  clearToken: () => localStorage.removeItem('token'),
  isAuthenticated: () => !!localStorage.getItem('token'),
}
