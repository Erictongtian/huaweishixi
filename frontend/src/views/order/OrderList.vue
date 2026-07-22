<template>
  <div class="order-list-page">
    <div class="page-header">
      <h2 class="page-title">我的订单</h2>
    </div>
    <div class="tabs-wrapper">
      <el-tabs v-model="activeRole" @tab-change="onRoleChange">
        <el-tab-pane label="我买到的" name="buyer" />
        <el-tab-pane label="我卖出的" name="seller" />
      </el-tabs>
    </div>

    <div class="filter-bar">
      <el-select v-model="statusFilter" placeholder="订单状态" clearable @change="fetchOrders">
        <el-option label="待确认" value="pending" />
        <el-option label="已确认" value="confirmed" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
    </div>

    <div v-loading="loading" class="order-list">
      <div v-for="order in orders" :key="order.id" class="order-card" @click="$router.push(`/orders/${order.id}`)">
        <div class="order-card-content">
          <div class="order-thumb-wrapper">
            <el-image :src="order.device_image_url || ''" fit="cover" class="order-thumb">
              <template #error><div class="thumb-placeholder">无图</div></template>
            </el-image>
          </div>
          <div class="order-info">
            <div class="order-title">{{ order.device_title || '设备' }}</div>
            <div class="order-meta">
              <span class="order-price">{{ formatPrice(parseFloat(order.price)) }}</span>
              <StatusTag :status="order.status" type="order" />
            </div>
            <div class="order-time">{{ formatDate(order.created_at) }}</div>
          </div>
          <div class="order-actions" @click.stop>
            <template v-if="isBuyer && order.status === 'pending'">
              <el-button size="small" type="danger" @click="handleCancel(order.id)">取消</el-button>
            </template>
            <template v-if="isSeller && order.status === 'pending'">
              <el-button size="small" type="primary" @click="handleConfirm(order.id)">确认</el-button>
              <el-button size="small" type="danger" @click="handleReject(order.id)">拒绝</el-button>
            </template>
            <template v-if="isBuyer && order.status === 'confirmed'">
              <el-button size="small" type="success" @click="handleComplete(order.id)">确认交付</el-button>
              <el-button size="small" type="danger" @click="handleCancel(order.id)">取消</el-button>
            </template>
            <template v-if="isSeller && order.status === 'confirmed'">
              <el-button size="small" type="danger" @click="handleCancel(order.id)">取消</el-button>
            </template>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    </div>

    <div v-if="pages > 1" class="pagination">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="fetchOrders" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getMyOrders, confirmOrder, rejectOrder, completeOrder, cancelOrder } from '../../api/order'
import type { OrderListItem } from '../../api/order'

import StatusTag from '../../components/StatusTag.vue'
import { formatPrice, formatDate } from '../../utils/format'


const loading = ref(false)
const orders = ref<OrderListItem[]>([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const activeRole = ref('buyer')
const statusFilter = ref('')

const isBuyer = computed(() => activeRole.value === 'buyer')
const isSeller = computed(() => activeRole.value === 'seller')

onMounted(fetchOrders)

async function fetchOrders() {
  loading.value = true
  try {
    const resp = await getMyOrders({ role: activeRole.value, status: statusFilter.value || undefined, page: page.value })
    const res = resp.data.data
    orders.value = res.items || []
    total.value = res.total || 0
    pages.value = res.pages || 0
  } catch (e: any) {
    ElMessage.error(e.message || '获取订单失败')
  } finally {
    loading.value = false
  }
}

function onRoleChange() {
  page.value = 1
  statusFilter.value = ''
  fetchOrders()
}

async function handleConfirm(id: string) {
  try { await confirmOrder(id); ElMessage.success('已确认'); fetchOrders() } catch (e: any) { ElMessage.error(e.message) }
}

async function handleReject(id: string) {
  try { await ElMessageBox.confirm('确定拒绝该订单？', '提示', { type: 'warning' }); await rejectOrder(id); ElMessage.success('已拒绝'); fetchOrders() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}

async function handleComplete(id: string) {
  try { await ElMessageBox.confirm('确认已收到设备？', '确认交付', { type: 'info' }); await completeOrder(id); ElMessage.success('已确认交付'); fetchOrders() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}

async function handleCancel(id: string) {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消订单', { inputPattern: /.+/, inputErrorMessage: '取消原因不能为空' })
    await cancelOrder(id, value)
    ElMessage.success('已取消')
    fetchOrders()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}
</script>

<style scoped>
.order-list-page {
  padding: 32px 24px;
  max-width: 900px;
  margin: 0 auto;
  animation: fadeInUp 0.5s ease-out;
}

.page-header {
  margin-bottom: 8px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0;
  color: var(--color-foreground);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.tabs-wrapper {
  margin-bottom: 16px;
}

.tabs-wrapper :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--color-border);
}

.tabs-wrapper :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  height: 3px;
  border-radius: 2px;
}

.tabs-wrapper :deep(.el-tabs__item.is-active) {
  color: var(--color-accent);
  font-weight: 600;
  font-family: var(--font-display);
}

.filter-bar {
  margin-bottom: 20px;
}

.filter-bar :deep(.el-input__wrapper) {
  border-radius: 20px !important;
  padding: 2px 14px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background: var(--color-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: var(--transition-normal);
  overflow: hidden;
}

.order-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--color-accent-secondary);
}

.order-card-content {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px 20px;
}

.order-thumb-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.order-thumb {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-sm);
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
  border-radius: var(--radius-sm);
}

.order-info {
  flex: 1;
  min-width: 0;
}

.order-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: 6px;
  font-family: var(--font-display);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.order-price {
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.order-time {
  font-size: 12px;
  color: var(--color-muted-foreground);
}

.order-actions {
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
