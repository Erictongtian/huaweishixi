<template>
  <div class="user-manage">
    <div class="page-header">
      <div>
        <h2>用户管理</h2>
        <p class="page-subtitle">管理平台用户账户</p>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索用户名或昵称" clearable size="large" class="search-input" @input="onSearch">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="statusFilter" placeholder="用户状态" clearable size="large" @change="fetchUsers">
        <el-option label="正常" value="active" />
        <el-option label="已封禁" value="locked" />
        <el-option label="已注销" value="disabled" />
      </el-select>
      <el-select v-model="roleFilter" placeholder="角色" clearable size="large" @change="fetchUsers">
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
    </div>

    <div class="table-wrapper">
      <el-table :data="users" v-loading="loading" stripe class="user-table">
        <el-table-column prop="username" label="用户名" min-width="100">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="28" :src="row.avatar || undefined" class="table-avatar">
                {{ row.nickname?.charAt(0) || '?' }}
              </el-avatar>
              <span class="user-cell-name">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" min-width="80" />
        <el-table-column prop="email" label="邮箱" min-width="220">
          <template #default="{ row }">
            <span class="mono-text email-text">{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="验证" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'warning'" size="small" effect="dark" round>
              {{ row.is_verified ? '已验证' : '未验证' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : ''" size="small" effect="dark" round>
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small" effect="dark" round>
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">
            <span class="mono-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.role !== 'admin'">
              <el-button v-if="row.status === 'active'" type="warning" link size="small" @click="handleBan(row)">封禁</el-button>
              <el-button v-if="row.status === 'locked'" type="success" link size="small" @click="handleUnban(row)">解封</el-button>
              <el-button v-if="row.status !== 'disabled'" type="primary" link size="small" @click="handleResetPwd(row)">重置密码</el-button>
              <el-button v-if="row.status !== 'disabled'" type="danger" link size="small" @click="handleDelete(row)">注销</el-button>
            </template>
            <span v-else class="no-action">-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="pages > 1" class="pagination">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next" @current-change="fetchUsers" />
    </div>

    <el-dialog v-model="pwdDialogVisible" title="重置用户密码" width="440px">
      <p class="pwd-dialog-tip">为用户「{{ pwdTargetUser?.nickname || pwdTargetUser?.username }}」设置新密码</p>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password size="large" placeholder="8-20位，包含字母和数字" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password size="large" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSubmitting" @click="handlePwdSubmit">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { getAdminUsers, banUser, unbanUser, deleteUser, resetUserPassword } from '../../api/admin'
import type { AdminUserItem } from '../../api/admin'
import { formatDate } from '../../utils/format'

const loading = ref(false)
const users = ref<AdminUserItem[]>([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const size = ref(20)
const keyword = ref('')
const statusFilter = ref('')
const roleFilter = ref('')

let searchTimer: ReturnType<typeof setTimeout> | null = null

const pwdDialogVisible = ref(false)
const pwdSubmitting = ref(false)
const pwdTargetUser = ref<AdminUserItem | null>(null)
const pwdFormRef = ref<FormInstance>()
const pwdForm = reactive({ new_password: '', confirm_password: '' })

const validateConfirm = (_rule: any, value: string, callback: any) => {
  if (value !== pwdForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const pwdRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码须8-20位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码须包含字母和数字', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

onMounted(() => fetchUsers())

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchUsers() }, 300)
}

async function fetchUsers() {
  loading.value = true
  try {
    const resp = await getAdminUsers({
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined,
      role: roleFilter.value || undefined,
      page: page.value,
      size: size.value,
    })
    const d = resp.data.data
    users.value = d.items || []
    total.value = d.total || 0
    pages.value = d.pages || 0
  } catch (e: any) {
    ElMessage.error(e.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function statusTagType(status: string) {
  const map: Record<string, string> = { active: 'success', locked: 'warning', disabled: 'info' }
  return map[status] || 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = { active: '正常', locked: '已封禁', disabled: '已注销' }
  return map[status] || status
}

async function handleBan(user: AdminUserItem) {
  try {
    await ElMessageBox.confirm(`确定封禁用户「${user.nickname || user.username}」？封禁后该用户将无法登录`, '封禁用户', { type: 'warning' })
    await banUser(user.id)
    ElMessage.success('已封禁')
    fetchUsers()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  }
}

async function handleUnban(user: AdminUserItem) {
  try {
    await unbanUser(user.id)
    ElMessage.success('已解封')
    fetchUsers()
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

async function handleDelete(user: AdminUserItem) {
  try {
    await ElMessageBox.confirm(`确定注销用户「${user.nickname || user.username}」？该操作不可恢复，其所有在售设备将下架，活跃订单将取消`, '注销用户', { type: 'error' })
    await deleteUser(user.id)
    ElMessage.success('已注销')
    fetchUsers()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  }
}

function handleResetPwd(user: AdminUserItem) {
  pwdTargetUser.value = user
  pwdForm.new_password = ''
  pwdForm.confirm_password = ''
  pwdDialogVisible.value = true
}

async function handlePwdSubmit() {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return

  pwdSubmitting.value = true
  try {
    await resetUserPassword(pwdTargetUser.value!.id, pwdForm.new_password)
    ElMessage.success('密码重置成功')
    pwdDialogVisible.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '重置失败')
  } finally {
    pwdSubmitting.value = false
  }
}
</script>

<style scoped>
.user-manage {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px;
  animation: fadeInUp 0.5s ease-out;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 26px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-muted-foreground);
  margin: 4px 0 0;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  width: 260px;
}

.filter-bar :deep(.el-input__wrapper),
.filter-bar :deep(.el-select .el-input__wrapper) {
  border-radius: 20px !important;
}

.table-wrapper {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.user-table {
  --el-table-border-color: var(--color-border);
  --el-table-header-bg-color: var(--color-muted);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-avatar {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  font-family: var(--font-display);
  font-weight: 700;
  flex-shrink: 0;
}

.user-cell-name {
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-foreground);
}

.mono-text {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--color-muted-foreground);
}

.email-text {
  white-space: nowrap;
}

.no-action {
  color: var(--color-muted-foreground);
}

.pwd-dialog-tip {
  font-size: 14px;
  color: var(--color-foreground);
  margin: 0 0 16px;
  font-weight: 500;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}
</style>