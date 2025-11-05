import api from './api'
import type { LoginCredentials, LoginResponse, TokenRefreshResponse, User } from '@/types'

export const authService = {
  /**
   * Login with email/username and password
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login/', credentials)
    const { access, refresh, user } = response.data

    // Store tokens
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('user', JSON.stringify(user))

    return response.data
  },

  /**
   * Logout - blacklist refresh token
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await api.post('/auth/logout/', { refresh: refreshToken })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    // Clear local storage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await api.post<TokenRefreshResponse>('/auth/refresh/', {
      refresh: refreshToken,
    })

    const { access } = response.data
    localStorage.setItem('access_token', access)

    return access
  },

  /**
   * Get current user from API
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me/')
    const user = response.data

    // Update stored user
    localStorage.setItem('user', JSON.stringify(user))

    return user
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },

  /**
   * Get stored user from localStorage
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null

    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  },

  /**
   * Test token validity
   */
  async testToken(): Promise<boolean> {
    try {
      await api.get('/auth/test/')
      return true
    } catch {
      return false
    }
  },
}
