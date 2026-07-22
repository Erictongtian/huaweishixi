<template>
  <div class="my-devices-page">
    <div class="page-header">
      <h2>我的发布</h2>
    </div>

    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="onFilterChange" class="status-radio-group">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="on_sale">在售</el-radio-button>
        <el-radio-button value="off_shelf">已下架</el-radio-button>
        <el-radio-button value="sold">已售出</el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading" class="device-list">
      <div v-for="device in devices" :key="device.id" class="my-device-card">
        <div class="device-thumb-wrapper">
          <el-image :src="device.image_url || ''" fit="cover" class="device-thumb">
            <template #error><div class="thumb-placeholder">无图</div></template>
          </el-image>
        </div>
        <div class="device-info">
          <div class="device-title">{{ device.title }}</div>
          <div class="device-meta">
            <span class="device-price">{{ formatPrice(device.price) }}</span>
            <StatusTag :status="device.status" type="device" />
          </div>
          <div class="device-extra">
            <span>{{ conditionLevelMap[device.condition_level] || device.condition_level }}</span>
            <span v-if="device.location">{{ device.location }}</span>
          </div>
        </div>
        <div class="device-actions">
          <el-button v-if="device.status === 'on_sale'" type="warning" size="small" @click="handleToggleStatus(device, 'off_shelf')">下架</el-button>
          <el-button v-if="device.status === 'off_shelf'" type="success" size="small" @click="handleToggleStatus(device, 'on_sale')">上架</el-button>
          <el-button v-if="device.status !== 'sold'" type="primary" size="small" @click="$router.push(`/devices/publish?edit=${device.id}`)">编辑</el-button>
          <el-button v-if="device.status === 'off_shelf'" type="danger" size="small" @click="handleDelete(device)">删除</el-button>
        </div>
      </div>
      <el-empty v-if="!loading && devices.length === 0" description="暂无设备" />
    </div>

    <div v-if="pages > 1" class="pagination">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next" @current-change="fetchDevices" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyDevices } from '../../api/user'
import type { MyDeviceItem } from '../../api/user'
import { toggleStatus, deleteDevice } from '../../api/device'
import StatusTag from '../../components/StatusTag.vue'
import { formatPrice, conditionLevelMap } from '../../utils/format'

const loading = ref(false)
const devices = ref<MyDeviceItem[]>([])
const statusFilter = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)
const pages = ref(0)

onMounted(() => fetchDevices())

async function fetchDevices() {
  loading.value = true
  try {
    const resp = await getMyDevices({ status: statusFilter.value || undefined, page: page.value, size: size.value })
    const d = resp.data.data
    devices.value = d.items
    total.value = d.total
    pages.value = d.pages
  } catch (e: any) {
    ElMessage.error(e.message || '获取设备失败')
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  fetchDevices()
}

async function handleToggleStatus(device: MyDeviceItem, newStatus: string) {
  try {
    await toggleStatus(device.id, newStatus)
    device.status = newStatus
    ElMessage.success(newStatus === 'on_sale' ? '已上架' : '已下架')
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

async function handleDelete(device: MyDeviceItem) {
  try {
    await ElMessageBox.confirm(`确定删除「${device.title}」？`, '提示', { type: 'warning' })
    await deleteDevice(device.id)
    ElMessage.success('已删除')
    await fetchDevices()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}
</script>

<style scoped>
.my-devices-page {
  max-width: 900px;
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

.filter-bar {
  margin-bottom: 20px;
}

.status-radio-group :deep(.el-radio-button__inner) {
  border-radius: 20px !important;
  border: none !important;
  background: var(--color-muted);
  color: var(--color-muted-foreground);
  font-weight: 500;
  font-family: var(--font-display);
  box-shadow: none !important;
  padding: 8px 20px;
}

.status-radio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  box-shadow: var(--shadow-accent) !important;
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.my-device-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-normal);
}

.my-device-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--color-accent-secondary);
}

.device-thumb-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.device-thumb {
  width: 80px;
  height: 80px;
}

.thumb-placeholder {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-muted);
  color: var(--color-muted-foreground);
  font-size: 12px;
}

.device-info {
  flex: 1;
  min-width: 0;
}

.device-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: 6px;
  font-family: var(--font-display);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.device-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.device-price {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.device-extra {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-muted-foreground);
}

.device-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}
</style>
