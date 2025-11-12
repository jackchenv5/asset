import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, logout, getUserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  const loginAction = async (loginForm) => {
    try {
      const response = await login(loginForm)
      isAuthenticated.value = true
      return response
    } catch (error) {
      throw error
    }
  }

  const logoutAction = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      isAuthenticated.value = false
    }
  }

  const getUserInfoAction = async () => {
    try {
      const response = await getUserInfo()
      user.value = response.data.user
      isAuthenticated.value = true
      return response
    } catch (error) {
      throw error
    }
  }

  return {
    user,
    isAuthenticated,
    loginAction,
    logoutAction,
    getUserInfoAction
  }
})