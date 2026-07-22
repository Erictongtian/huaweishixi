import request from '../utils/request'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  password: string
  nickname: string
  email?: string
  phone?: string
}

export interface UserInfo {
  id: string
  username: string
  nickname: string
  email: string | null
  phone: string | null
  role: string
  avatar: string | null
  created_at: string
}

export interface TokenData {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

export function login(data: LoginData) {
  return request.post<{ code: number; message: string; data: TokenData }>('/auth/login', data)
}

export function register(data: RegisterData) {
  return request.post<{ code: number; message: string; data: UserInfo }>('/auth/register', data)
}

export function refreshToken(token: string) {
  return request.post<{ code: number; message: string; data: { access_token: string; token_type: string; expires_in: number } }>(
    '/auth/refresh',
    null,
    { headers: { Authorization: `Bearer ${token}` } }
  )
}

export function getMe() {
  return request.get<{ code: number; message: string; data: UserInfo }>('/auth/me')
}