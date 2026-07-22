import request from '../utils/request'

export interface CategoryItem {
  id: string
  name: string
  icon: string | null
  sort_order: number
  status: string
  device_count: number
}

export interface CategoryCreate {
  name: string
  icon?: string
  sort_order?: number
}

export interface CategoryUpdate {
  name?: string
  icon?: string
  sort_order?: number
}

export function getCategories() {
  return request.get('/categories')
}

export function createCategory(data: CategoryCreate) {
  return request.post('/categories', data)
}

export function updateCategory(id: string, data: CategoryUpdate) {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id: string) {
  return request.delete(`/categories/${id}`)
}
