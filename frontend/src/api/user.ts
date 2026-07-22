import request from '../utils/request'

export interface ProfileUpdate {
  nickname?: string
  phone?: string
  email?: string
  avatar?: string
}

export interface ChangePassword {
  old_password: string
  new_password: string
}

export interface MyDeviceItem {
  id: string
  title: string
  price: number
  original_price: number | null
  condition_level: string
  status: string
  view_count: number
  location: string | null
  created_at: string | null
  image_url: string | null
  category_id: string
}

export function updateProfile(data: ProfileUpdate) {
  return request.put('/users/me', data)
}

export function changePassword(data: ChangePassword) {
  return request.put('/users/me/password', data)
}

export function getMyDevices(params?: { status?: string; page?: number; size?: number }) {
  return request.get('/users/me/devices', { params })
}