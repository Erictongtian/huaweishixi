<template>
  <div class="register-page">
    <div class="register-bg-accent" />
    <div class="register-container">
      <div class="register-left">
        <div class="brand-section">
          <div class="brand-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="white" fill-opacity="0.2"/>
              <path d="M16 18L24 14L32 18V26L24 34L16 26V18Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
              <circle cx="24" cy="24" r="4" stroke="white" stroke-width="2"/>
            </svg>
          </div>
          <h1 class="brand-title">加入我们</h1>
          <h2 class="brand-subtitle">开启校园交易之旅</h2>
          <p class="brand-desc">注册账号，发布你的闲置设备，发现超值好物</p>
          <div class="brand-features">
            <div class="feature-item">
              <span class="feature-dot" />
              <span>免费发布闲置设备</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>智能搜索与筛选</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>安全便捷的交易流程</span>
            </div>
          </div>
        </div>
      </div>
      <div class="register-right">
        <div class="register-card">
          <h2 class="register-title">创建账号</h2>
          <p class="register-subtitle">填写以下信息完成注册</p>
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleRegister">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="3-20位，字母、数字、下划线" size="large" data-testid="input-username">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="form.nickname" placeholder="请输入昵称" size="large" data-testid="input-nickname">
                <template #prefix>
                  <el-icon><Avatar /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="8-20位，包含字母和数字" size="large" show-password data-testid="input-password">
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" size="large" show-password data-testid="input-confirm-password">
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <div class="optional-row">
              <el-form-item label="邮箱（选填）" prop="email" class="optional-item">
                <el-input v-model="form.email" placeholder="请输入邮箱" size="large" data-testid="input-email">
                  <template #prefix>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="手机号（选填）" prop="phone" class="optional-item">
                <el-input v-model="form.phone" placeholder="请输入手机号" size="large" data-testid="input-phone">
                  <template #prefix>
                    <el-icon><Phone /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>
            <el-form-item>
              <el-button type="primary" :loading="loading" class="register-btn" size="large" data-testid="btn-register" @click="handleRegister">
                注册
              </el-button>
            </el-form-item>
            <div class="register-footer">
              已有账号？<router-link to="/login">立即登录</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Avatar, Lock, Message, Phone } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名须3-20位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '仅含字母、数字、下划线', trigger: 'blur' },
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { max: 50, message: '昵称最长50个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码须8-20位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码须包含字母和数字', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.register({
      username: form.username,
      nickname: form.nickname,
      password: form.password,
      email: form.email || undefined,
      phone: form.phone || undefined,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e: any) {
    ElMessage.error(e.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-background);
  position: relative;
  overflow: hidden;
  padding: 32px 0;
}

.register-bg-accent {
  position: absolute;
  top: -30%;
  right: -20%;
  width: 70%;
  height: 160%;
  background: linear-gradient(135deg, #7C3AED 0%, var(--color-accent-secondary) 40%, var(--color-accent) 100%);
  border-radius: 60% 0 0 40%;
  z-index: 0;
}

.register-container {
  display: flex;
  width: 920px;
  min-height: 640px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

.register-left {
  width: 380px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #7C3AED 0%, var(--color-accent-secondary) 40%, var(--color-accent) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 36px;
  position: relative;
  overflow: hidden;
}

.register-left::before {
  content: '';
  position: absolute;
  bottom: -50%;
  left: -50%;
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

.register-right {
  flex: 1;
  background: var(--color-card);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 36px;
  overflow-y: auto;
}

.register-card {
  width: 100%;
  max-width: 420px;
}

.register-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.register-subtitle {
  font-size: 14px;
  color: var(--color-muted-foreground);
  margin: 0 0 28px;
}

.optional-row {
  display: flex;
  gap: 12px;
}

.optional-item {
  flex: 1;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-display);
  border-radius: var(--radius-md) !important;
  letter-spacing: 0.02em;
}

.register-footer {
  text-align: center;
  color: var(--color-muted-foreground);
  font-size: 14px;
  margin-top: 8px;
}

.register-footer a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition-fast);
}

.register-footer a:hover {
  color: var(--color-accent-secondary);
}

@media (max-width: 768px) {
  .register-left {
    display: none;
  }
  .register-container {
    width: 440px;
  }
}
</style>
