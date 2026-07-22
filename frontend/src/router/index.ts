import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const scrollPositions: Record<string, number> = {}

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    const saved = scrollPositions[to.fullPath]
    if (saved !== undefined) {
      return { top: saved }
    }
    return { top: 0 }
  },
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/auth/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/auth/Register.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('../views/device/DeviceList.vue'),
        },
        {
          path: 'devices/:id',
          name: 'DeviceDetail',
          component: () => import('../views/device/DeviceDetail.vue'),
        },
        {
          path: 'devices/publish',
          name: 'DevicePublish',
          component: () => import('../views/device/DevicePublish.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'orders',
          name: 'OrderList',
          component: () => import('../views/order/OrderList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'orders/:id',
          name: 'OrderDetail',
          component: () => import('../views/order/OrderDetail.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('../views/profile/Profile.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'my/devices',
          name: 'MyDevices',
          component: () => import('../views/my/MyDevices.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'admin/categories',
          name: 'CategoryManage',
          component: () => import('../views/admin/CategoryManage.vue'),
          meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'admin/users',
          name: 'UserManage',
          component: () => import('../views/admin/UserManage.vue'),
          meta: { requiresAuth: true, requiresAdmin: true },
        },
      ],
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  scrollPositions[_from.fullPath] = window.scrollY

  const authStore = useAuthStore()
  const token = localStorage.getItem('token')

  if (token && !authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch {
      authStore.logout()
    }
  }

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'Login' || to.name === 'Register') && token) {
    next({ name: 'Home' })
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next({ name: 'Home' })
  } else {
    next()
  }
})

router.afterEach((to) => {
  const saved = scrollPositions[to.fullPath]
  if (saved !== undefined) {
    requestAnimationFrame(() => {
      window.scrollTo(0, saved)
    })
  }
})

export default router
