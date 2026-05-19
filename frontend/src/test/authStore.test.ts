import { authStore } from '../store/authStore'

describe('authStore', () => {
  beforeEach(() => localStorage.clear())
  it('false when no token', () => expect(authStore.isAuthenticated()).toBe(false))
  it('true after setToken', () => {
    authStore.setToken('t')
    expect(authStore.isAuthenticated()).toBe(true)
  })
  it('getToken returns token', () => {
    authStore.setToken('abc')
    expect(authStore.getToken()).toBe('abc')
  })
  it('clearToken removes', () => {
    authStore.setToken('abc')
    authStore.clearToken()
    expect(authStore.isAuthenticated()).toBe(false)
  })
})
