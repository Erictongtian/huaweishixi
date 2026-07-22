<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <el-avatar :size="80" :src="authStore.user?.avatar || undefined" class="user-avatar">
            {{ authStore.user?.nickname?.charAt(0) || '?' }}
          </el-avatar>
        </div>
        <div class="user-meta">
          <h2>{{ authStore.user?.nickname }}</h2>
          <span class="username">@{{ authStore.user?.username }}</span>
        </div>
      </div>
    </div>

    <div class="profile-card">
      <div class="card-header">
        <div class="card-header-left">
          <div class="card-icon">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="6" r="3" stroke="currentColor" stroke-width="1.5"/>
              <path d="M2 14C2 11 5 9 8 9C11 9 14 11 14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="card-title">基本信息</span>
        </div>
        <el-button v-if="!editing" type="primary" size="small" @click="editing = true">编辑</el-button>
        <div v-else class="edit-actions">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </div>
      <el-form label-width="80px" class="profile-form">
        <el-form-item label="昵称">
          <el-input v-if="editing" v-model="form.nickname" maxlength="50" size="large" />
          <span v-else class="form-value">{{ authStore.user?.nickname || '-' }}</span>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-if="editing" v-model="form.phone" placeholder="选填" size="large" />
          <span v-else class="form-value">{{ authStore.user?.phone || '-' }}</span>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-if="editing" v-model="form.email" placeholder="选填" size="large" />
          <span v-else class="form-value">{{ authStore.user?.email || '-' }}</span>
        </el-form-item>
        <el-form-item v-if="editing" label="头像">
          <div v-if="editing" class="avatar-upload-area">
            <div v-if="avatarPreview" class="avatar-preview-item">
              <el-image :src="avatarPreview" fit="cover" class="avatar-preview-img" />
              <div class="avatar-preview-actions">
                <el-icon @click.stop="removeAvatar"><Delete /></el-icon>
              </div>
            </div>
            <div v-if="!avatarPreview" class="avatar-upload-trigger" @click="triggerAvatarUpload">
              <el-icon :size="28"><Plus /></el-icon>
              <span>上传头像</span>
            </div>
            <input ref="avatarInput" type="file" accept="image/jpeg,image/png,image/gif,image/webp" class="hidden-input" @change="onAvatarChange" />
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div class="profile-card">
      <div class="card-header">
        <div class="card-header-left">
          <div class="card-icon">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="3" y="6" width="10" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M5 6V4C5 2.9 5.9 2 7 2H9C10.1 2 11 2.9 11 4V6" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="8" cy="10" r="1" fill="currentColor"/>
            </svg>
          </div>
          <span class="card-title">修改密码</span>
        </div>
      </div>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px" class="profile-form">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="changingPwd" @click="handleChangePwd">修改密码</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { updateProfile, changePassword } from '../../api/user'
import { uploadFile } from '../../api/review'

const authStore = useAuthStore()

const editing = ref(false)
const saving = ref(false)
const changingPwd = ref(false)
const uploadingAvatar = ref(false)
const avatarInput = ref<HTMLInputElement>()

const avatarPreview = computed(() => form.avatar || authStore.user?.avatar || '')

const form = reactive({
  nickname: authStore.user?.nickname || '',
  phone: authStore.user?.phone || '',
  email: authStore.user?.email || '',
  avatar: authStore.user?.avatar || '',
})

const pwdFormRef = ref<FormInstance>()
const pwdForm = reactive({
  old_password: '',
  new_password: '',
})

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码须8-20位', trigger: 'blur' },
  ],
}

function cancelEdit() {
  form.nickname = authStore.user?.nickname || ''
  form.phone = authStore.user?.phone || ''
  form.email = authStore.user?.email || ''
  form.avatar = authStore.user?.avatar || ''
  editing.value = false
}

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

function removeAvatar() {
  form.avatar = ''
}

async function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片不能超过5MB')
    input.value = ''
    return
  }
  uploadingAvatar.value = true
  try {
    const resp = await uploadFile(file)
    form.avatar = resp.data.data.url
  } catch (err: any) {
    ElMessage.error(err.message || '上传失败')
  } finally {
    uploadingAvatar.value = false
    input.value = ''
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateProfile({
      nickname: form.nickname || undefined,
      phone: form.phone || undefined,
      email: form.email || undefined,
      avatar: form.avatar || undefined,
    })
    await authStore.fetchCurrentUser()
    ElMessage.success('更新成功')
    editing.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '更新失败')
  } finally {
    saving.value = false
  }
}

async function handleChangePwd() {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return

  changingPwd.value = true
  try {
    await changePassword({ old_password: pwdForm.old_password, new_password: pwdForm.new_password })
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    authStore.logout()
  } catch (e: any) {
    ElMessage.error(e.message || '修改失败')
  } finally {
    changingPwd.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 32px 24px;
  animation: fadeInUp 0.5s ease-out;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 28px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-wrapper {
  position: relative;
}

.user-avatar {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 32px;
}

.user-meta h2 {
  margin: 0;
  font-size: 24px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.username {
  font-size: 14px;
  color: var(--color-muted-foreground);
  font-family: var(--font-mono);
}

.profile-card {
  margin-bottom: 16px;
  padding: 24px;
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.form-value {
  font-size: 15px;
  color: var(--color-foreground);
  font-weight: 500;
}

.avatar-upload-area {
  display: flex;
  gap: 8px;
}

.avatar-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.avatar-preview-img {
  width: 100%;
  height: 100%;
}

.avatar-preview-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  padding: 4px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-preview-item:hover .avatar-preview-actions {
  opacity: 1;
}

.avatar-preview-actions .el-icon {
  cursor: pointer;
}

.avatar-upload-trigger {
  width: 100px;
  height: 100px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-muted-foreground);
  font-size: 12px;
  gap: 4px;
  transition: var(--transition-normal);
}

.avatar-upload-trigger:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(0, 82, 255, 0.04);
}

.hidden-input {
  display: none;
}
</style>
