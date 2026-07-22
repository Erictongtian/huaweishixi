<template>
  <div class="login-page">
    <div class="login-bg-accent" />
    <div class="login-container">
      <div class="login-left">
        <div class="brand-section">
          <div class="brand-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="white" fill-opacity="0.2"/>
              <path d="M16 18L24 14L32 18V26L24 34L16 26V18Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
              <circle cx="24" cy="24" r="4" stroke="white" stroke-width="2"/>
            </svg>
          </div>
          <h1 class="brand-title">校园二手设备</h1>
          <h2 class="brand-subtitle">交易平台</h2>
          <p class="brand-desc">让闲置焕发新生，让交易更加简单</p>
          <div class="brand-features">
            <div class="feature-item">
              <span class="feature-dot" />
              <span>安全可靠的交易保障</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>便捷的设备搜索</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>真实的用户评价体系</span>
            </div>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-card">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">登录你的账号继续使用</p>
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" size="large" data-testid="input-username">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password data-testid="input-password" @keyup.enter="handleLogin">
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" class="login-btn" size="large" data-testid="btn-login" @click="handleLogin">
                登录
              </el-button>
            </el-form-item>
            <div class="login-footer">
              还没有账号？<router-link to="/register">立即注册</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login({ username: form.username, password: form.password })
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-background);
  position: relative;
  overflow: hidden;
}

.login-bg-accent {
  position: absolute;
  top: -30%;
  left: -20%;
  width: 70%;
  height: 160%;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 60%, #7C3AED 100%);
  border-radius: 0 0 60% 40%;
  z-index: 0;
}

.login-container {
  display: flex;
  width: 900px;
  min-height: 560px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

.login-left {
  width: 400px;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 60%, #7C3AED 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
}

.brand-section {
  position: relative;
  z-index: 1;
  color: white;
}

.brand-icon {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 16px;
  font-family: var(--font-display);
  letter-spacing: -0.02em;
  opacity: 0.9;
}

.brand-desc {
  font-size: 15px;
  margin: 0 0 32px;
  opacity: 0.8;
  line-height: 1.6;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.9;
}

.feature-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
  flex-shrink: 0;
}

.login-right {
  flex: 1;
  background: var(--color-card);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
}

.login-card {
  width: 100%;
  max-width: 360px;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.login-subtitle {
  font-size: 14px;
  color: var(--color-muted-foreground);
  margin: 0 0 32px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-display);
  border-radius: var(--radius-md) !important;
  letter-spacing: 0.02em;
}

.login-footer {
  text-align: center;
  color: var(--color-muted-foreground);
  font-size: 14px;
  margin-top: 8px;
}

.login-footer a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition-fast);
}

.login-footer a:hover {
  color: var(--color-accent-secondary);
}

@media (max-width: 768px) {
  .login-left {
    display: none;
  }
  .login-container {
    width: 420px;
  }
}
</style>
