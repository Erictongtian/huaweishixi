import { describe, it, expect } from 'vitest'
import { formatPrice, formatDate, deviceStatusMap, orderStatusMap, conditionLevelMap } from '../utils/format'

describe('formatPrice', () => {
  it('formats price with 2 decimals', () => {
    expect(formatPrice(99.5)).toBe('¥99.50')
  })
  it('formats zero', () => {
    expect(formatPrice(0)).toBe('¥0.00')
  })
  it('formats large price', () => {
    expect(formatPrice(12345.67)).toBe('¥12345.67')
  })
})

describe('formatDate', () => {
  it('formats ISO date string', () => {
    const result = formatDate('2026-07-20T12:00:00Z')
    expect(result).toContain('2026')
  })
  it('returns empty for empty string', () => {
    expect(formatDate('')).toBe('')
  })
})

describe('deviceStatusMap', () => {
  it('maps on_sale', () => {
    expect(deviceStatusMap.on_sale).toBe('在售')
  })
  it('maps off_shelf', () => {
    expect(deviceStatusMap.off_shelf).toBe('已下架')
  })
  it('maps sold', () => {
    expect(deviceStatusMap.sold).toBe('已售出')
  })
})

describe('orderStatusMap', () => {
  it('maps pending', () => {
    expect(orderStatusMap.pending).toBe('待确认')
  })
  it('maps completed', () => {
    expect(orderStatusMap.completed).toBe('已完成')
  })
})

describe('conditionLevelMap', () => {
  it('maps almost_new', () => {
    expect(conditionLevelMap.almost_new).toBe('几乎全新')
  })
  it('maps good', () => {
    expect(conditionLevelMap.good).toBe('成色良好')
  })
})