import request from '../utils/request'

export interface ReviewCreate {
  order_id: string
  rating: number
  content?: string
  images?: string[]
}

export interface ReviewItem {
  id: string
  order_id: string
  device_id: string
  reviewer_id: string
  rating: number
  content: string | null
  images: string[] | null
  created_at: string
  updated_at: string
  reviewer_nickname: string | null
  reviewer_avatar: string | null
}

export interface ReviewStats {
  avg_rating: number
  total_reviews: number
  rating_distribution: Record<string, number>
}

export function createReview(data: ReviewCreate) {
  return request.post('/reviews', data)
}

export function getDeviceReviews(deviceId: string, params?: { page?: number; size?: number }) {
  return request.get(`/devices/${deviceId}/reviews`, { params })
}

export function getUserReviewStats(userId: string) {
  return request.get(`/users/${userId}/review-stats`)
}

export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}