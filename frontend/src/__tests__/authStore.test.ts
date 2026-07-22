import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../stores/auth'

vi.mock('../api/auth', () => ({
  login: vi.fn().mockResolvedValue({
    data: {
      data: {
        access_token: 'test-at',
        refresh_token: 'test-rt',
        expires_in: 3600,
        user: { id: '1', username: 'test', nickname: 'Test', email: null, phone: null, role: 'user', avatar: null, created_at: '2026-01-01' },
      },
    },
  }),
  register: vi.fn().mockResolvedValue({ data: { code: 201 } }),
  refreshToken: vi.fn().mockResolvedValue({
    data: { data: { access_token: 'new-at', token_type: 'Bearer', expires_in: 3600 } },
  }),
  getMe: vi.fn().mockResolvedValue({
    data: {
      data: { id: '1', username: 'test', nickname: 'Test', email: null, phone: null, role: 'user', avatar: null, created_at: '2026-01-01' },
    },
  }),
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('initial state', () => {
    const store = useAuthStore()
    expect(store.user).toBeNull()
    expect(store.isLoggedIn).toBe(false)
    expect(store.isAdmin).toBe(false)
  })

  it('login sets token and user', async () => {
    const store = useAuthStore()
    await store.login({ username: 'test', password: 'Test123456' })
    expect(store.token).toBe('test-at')
    expect(store.user?.nickname).toBe('Test')
    expect(store.isLoggedIn).toBe(true)
  })

  it('logout clears state', async () => {
    const store = useAuthStore()
    await store.login({ username: 'test', password: 'Test123456' })
    store.logout()
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })

  it('setToken updates localStorage', () => {
    const store = useAuthStore()
    store.setToken('new-token')
    expect(localStorage.getItem('token')).toBe('new-token')
  })

  it('isAdmin returns true for admin role', async () => {
    const { login: loginApi } = await import('../api/auth')
    vi.mocked(loginApi).mockResolvedValueOnce({
      data: {
        data: {
          access_token: 'at',
          refresh_token: 'rt',
          expires_in: 3600,
          user: { id: '2', username: 'admin', nickname: 'Admin', email: null, phone: null, role: 'admin', avatar: null, created_at: '2026-01-01' },
        },
      },
    } as any)
    const store = useAuthStore()
    await store.login({ username: 'admin', password: 'Admin123456' })
    expect(store.isAdmin).toBe(true)
  })
})