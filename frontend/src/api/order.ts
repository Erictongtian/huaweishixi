import request from '../utils/request'

export interface OrderCreate {
  device_id: string
  buyer_message?: string
}

export interface OrderDetail {
  id: string
  order_no: string
  device_id: string
  buyer_id: string
  seller_id: string
  price: string
  status: string
  buyer_message: string | null
  seller_remark: string | null
  confirmed_at: string | null
  completed_at: string | null
  cancelled_at: string | null
  cancel_reason: string | null
  created_at: string
  updated_at: string
  device: { id: string; title: string; price: number; image_url: string | null } | null
  buyer: { id: string; username: string; nickname: string } | null
  seller: { id: string; username: string; nickname: string } | null
}

export interface OrderListItem {
  id: string
  order_no: string
  device_id: string
  buyer_id: string
  seller_id: string
  price: string
  status: string
  created_at: string
  device_title: string | null
  device_image_url: string | null
}

export function createOrder(data: OrderCreate) {
  return request.post('/orders', data)
}

export function getMyOrders(params: { role?: string; status?: string; page?: number; size?: number }) {
  return request.get('/orders', { params })
}

export function getOrderDetail(id: string) {
  return request.get(`/orders/${id}`)
}

export function confirmOrder(id: string, seller_remark?: string) {
  return request.patch(`/orders/${id}/confirm`, { seller_remark })
}

export function rejectOrder(id: string) {
  return request.patch(`/orders/${id}/reject`)
}

export function completeOrder(id: string) {
  return request.patch(`/orders/${id}/complete`)
}

export function cancelOrder(id: string, cancel_reason: string) {
  return request.patch(`/orders/${id}/cancel`, { cancel_reason })
}