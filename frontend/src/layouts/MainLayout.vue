<template>
  <el-container class="main-layout">
    <header class="main-header">
      <div class="header-inner">
        <div class="header-left">
          <router-link to="/" class="logo">
            <span class="logo-icon">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <rect x="2" y="6" width="16" height="16" rx="3" fill="url(#grad)" />
                <rect x="10" y="2" width="16" height="16" rx="3" fill="url(#grad)" opacity="0.6" />
                <defs><linearGradient id="grad" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#0052FF" /><stop offset="1" stop-color="#4D7CFF" /></linearGradient></defs>
              </svg>
            </span>
            <span class="logo-text">校园二手交易</span>
          </router-link>
        </div>
        <div class="header-center">
          <el-input placeholder="搜索设备..." class="search-input" :prefix-icon="Search" @keyup.enter="handleSearch" v-model="searchKeyword" />
        </div>
        <div class="header-right">
          <template v-if="authStore.isLoggedIn">
            <el-button type="primary" @click="$router.push('/devices/publish')">
              <el-icon style="margin-right: 4px;"><Plus /></el-icon>发布设备
            </el-button>
            <el-dropdown>
              <span class="user-menu">
                <el-avatar :size="34" :src="authStore.user?.avatar || undefined" class="user-avatar">
                  {{ authStore.user?.nickname?.charAt(0) || '?' }}
                </el-avatar>
                <span class="user-name">{{ authStore.user?.nickname }}</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/my/devices')">
                    <el-icon><Box /></el-icon>我的发布
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/orders')">
                    <el-icon><List /></el-icon>我的订单
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" divided @click="$router.push('/admin/categories')">
                    <el-icon><Setting /></el-icon>分类管理
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" @click="$router.push('/admin/users')">
                    <el-icon><UserFilled /></el-icon>用户管理
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Search, Plus, ArrowDown, User, Box, List, Setting, SwitchButton, UserFilled } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const searchKeyword = ref('')

function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/', query: { keyword: searchKeyword.value.trim() } })
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定退出登录吗？', '退出确认', { type: 'warning', confirmButtonText: '退出', cancelButtonText: '取消' })
    authStore.logout()
    router.push('/login')
  } catch { /* cancel */ }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
}
.main-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  transition: var(--transition-normal);
}
.logo:hover {
  transform: scale(1.02);
}
.logo-icon {
  display: flex;
  align-items: center;
}
.logo-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}
.search-input {
  width: 420px;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  background: var(--color-muted);
  box-shadow: none;
  padding: 4px 16px;
  transition: var(--transition-normal);
}
.search-input :deep(.el-input__wrapper:focus-within) {
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.12);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-menu {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 24px;
  transition: var(--transition-normal);
}
.user-menu:hover {
  background: var(--color-muted);
}
.user-avatar {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-secondary));
  color: #fff;
  font-family: var(--font-display);
  font-weight: 600;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-foreground);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.arrow-icon {
  font-size: 12px;
  color: var(--color-muted-foreground);
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  width: 100%;
}
</style>
