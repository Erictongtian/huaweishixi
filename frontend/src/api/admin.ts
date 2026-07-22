import request from '../utils/request'

export interface AdminUserItem {
  id: string
  username: string
  nickname: string
  email: string | null
  phone: string | null
  avatar: string | null
  role: string
  status: string
  created_at: string
}

export interface AdminUserListParams {
  keyword?: string
  status?: string
  role?: string
  page?: number
  size?: number
}

export function getAdminUsers(params?: AdminUserListParams) {
  return request.get('/admin/users', { params })
}

export function banUser(userId: string) {
  return request.patch(`/admin/users/${userId}/ban`)
}

export function unbanUser(userId: string) {
  return request.patch(`/admin/users/${userId}/unban`)
}

export function deleteUser(userId: string) {
  return request.delete(`/admin/users/${userId}`)
}

export function resetUserPassword(userId: string, newPassword: string) {
  return request.put(`/admin/users/${userId}/password`, { new_password: newPassword })
}