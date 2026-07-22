import request from '../utils/request'

export interface DeviceListItem {
  id: string
  title: string
  price: string
  original_price: string | null
  condition_level: string
  status: string
  view_count: number
  location: string | null
  created_at: string
  image_url: string | null
  category_name: string | null
  seller_nickname: string | null
}

export interface DeviceListParams {
  page?: number
  size?: number
  keyword?: string
  category?: string
  condition_level?: string
  min_price?: number
  max_price?: number
  sort?: string
  order?: string
}

export interface DeviceImage {
  id: string
  url: string
  sort_order: number
}

export interface DeviceDetail {
  id: string
  title: string
  description: string | null
  category_id: string
  price: string
  original_price: string | null
  usage_duration: string | null
  condition_level: string
  status: string
  seller_id: string
  view_count: number
  location: string | null
  contact_info: string | null
  created_at: string
  updated_at: string
  images: DeviceImage[]
  category: { id: string; name: string } | null
  seller: { id: string; username: string; nickname: string; avatar: string | null } | null
}

export function getDeviceList(params?: DeviceListParams) {
  return request.get('/devices', { params })
}

export function getDeviceDetail(id: string) {
  return request.get(`/devices/${id}`)
}

export function publishDevice(data: FormData) {
  return request.post('/devices', data, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export function updateDevice(id: string, data: Record<string, unknown>) {
  return request.put(`/devices/${id}`, data)
}

export function updatePrice(id: string, price: number) {
  return request.patch(`/devices/${id}/price`, { price })
}

export function toggleStatus(id: string, action: string) {
  return request.patch(`/devices/${id}/status`, { action })
}

export function deleteDevice(id: string) {
  return request.delete(`/devices/${id}`)
}

export function uploadDeviceImage(id: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/devices/${id}/images`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export function deleteDeviceImage(deviceId: string, imageId: string) {
  return request.delete(`/devices/${deviceId}/images/${imageId}`)
}

export function reorderDeviceImages(deviceId: string, imageIds: string[]) {
  return request.put(`/devices/${deviceId}/images/reorder`, { image_ids: imageIds })
}
