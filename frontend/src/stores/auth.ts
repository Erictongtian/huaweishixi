import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, refreshToken as refreshTokenApi, getMe } from '../api/auth'
import type { LoginData, RegisterData, UserInfo } from '../api/auth'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshTokenVal = ref<string | null>(localStorage.getItem('refreshToken'))
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setRefreshToken(newRefreshToken: string) {
    refreshTokenVal.value = newRefreshToken
    localStorage.setItem('refreshToken', newRefreshToken)
  }

  async function login(data: LoginData) {
    const resp = await loginApi(data)
    const res = resp.data.data
    setToken(res.access_token)
    setRefreshToken(res.refresh_token)
    user.value = res.user
  }

  async function register(data: RegisterData) {
    const resp = await registerApi(data)
    return resp.data.data
  }

  async function fetchCurrentUser() {
    const resp = await getMe()
    user.value = resp.data.data
  }

  function logout() {
    user.value = null
    token.value = null
    refreshTokenVal.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    router.push('/login')
  }

  async function refreshAccessToken() {
    if (!refreshTokenVal.value) return
    const resp = await refreshTokenApi(refreshTokenVal.value)
    setToken(resp.data.data.access_token)
  }

  return {
    user,
    token,
    refreshTokenVal,
    isLoggedIn,
    isAdmin,
    setToken,
    setRefreshToken,
    login,
    register,
    fetchCurrentUser,
    logout,
    refreshAccessToken,
  }
})
