export function formatPrice(price: number): string {
  return `¥${price.toFixed(2)}`
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export const deviceStatusMap: Record<string, string> = {
  on_sale: '在售',
  off_shelf: '已下架',
  sold: '已售出',
}

export const orderStatusMap: Record<string, string> = {
  pending: '待确认',
  confirmed: '已确认',
  completed: '已完成',
  cancelled: '已取消',
}

export const conditionLevelMap: Record<string, string> = {
  almost_new: '几乎全新',
  good: '成色良好',
  fair: '一般',
  poor: '较差',
}