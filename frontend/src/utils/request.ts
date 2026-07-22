import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let isRefreshing = false

request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message } = response.data
    if (code && code !== 200 && code !== 201) {
      return Promise.reject(new Error(message || '请求失败'))
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      const authStore = useAuthStore()
      if (!isRefreshing && authStore.refreshTokenVal) {
        isRefreshing = true
        originalRequest._retry = true
        try {
          const response = await axios.post('/api/v1/auth/refresh', null, {
            headers: { Authorization: `Bearer ${authStore.refreshTokenVal}` },
          })
          const { access_token } = response.data.data
          authStore.setToken(access_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return request(originalRequest)
        } catch {
          authStore.logout()
          router.push('/login')
          return Promise.reject(error)
        } finally {
          isRefreshing = false
        }
      } else {
        authStore.logout()
        router.push('/login')
      }
    }
    const msg = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

export default request
