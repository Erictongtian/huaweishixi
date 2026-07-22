<template>
  <div v-loading="loading" class="order-detail">
    <template v-if="order">
      <div class="detail-header">
        <el-page-header @back="$router.back()" title="返回">
          <template #content>
            <span class="order-no">订单 {{ order.order_no }}</span>
          </template>
        </el-page-header>
        <StatusTag :status="order.status" type="order" class="header-status" />
      </div>

      <div class="status-steps-wrapper">
        <el-steps :active="stepActive" finish-status="success" align-center>
          <el-step title="下单" />
          <el-step title="已确认" />
          <el-step title="已完成" />
        </el-steps>
      </div>

      <div class="info-card">
        <div class="card-header">
          <div class="card-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <rect x="2" y="2" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="6.5" cy="6.5" r="1.5" fill="currentColor"/>
              <path d="M2 12L6 8L9 10L12 7L16 11" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="card-title">设备信息</span>
        </div>
        <div class="device-info" @click="$router.push(`/devices/${order.device_id}`)">
          <div class="device-thumb-wrapper">
            <el-image :src="order.device?.image_url || ''" fit="cover" class="device-thumb">
              <template #error><div class="thumb-placeholder">无图</div></template>
            </el-image>
          </div>
          <div class="device-meta">
            <div class="device-title">{{ order.device?.title || '设备' }}</div>
            <div class="device-price">{{ formatPrice(parseFloat(order.price)) }}</div>
          </div>
        </div>
      </div>

      <div class="info-card">
        <div class="card-header">
          <div class="card-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M3 5H15V14H3V5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M3 8H15" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 5V14" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <span class="card-title">交易信息</span>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">订单编号</span>
            <span class="info-value mono">{{ order.order_no }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">订单状态</span>
            <span class="info-value"><StatusTag :status="order.status" type="order" /></span>
          </div>
          <div class="info-item">
            <span class="info-label">买家</span>
            <span class="info-value">{{ order.buyer?.nickname || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">卖家</span>
            <span class="info-value">{{ order.seller?.nickname || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">买家留言</span>
            <span class="info-value">{{ order.buyer_message || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">卖家备注</span>
            <span class="info-value">{{ order.seller_remark || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">下单时间</span>
            <span class="info-value mono">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">确认时间</span>
            <span class="info-value mono">{{ order.confirmed_at ? formatDate(order.confirmed_at) : '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">完成时间</span>
            <span class="info-value mono">{{ order.completed_at ? formatDate(order.completed_at) : '-' }}</span>
          </div>
          <div v-if="order.cancel_reason" class="info-item full-width">
            <span class="info-label">取消原因</span>
            <span class="info-value cancel-reason">{{ order.cancel_reason }}</span>
          </div>
        </div>
      </div>

      <div v-if="order.status !== 'completed' && order.status !== 'cancelled'" class="action-bar">
        <template v-if="isBuyer">
          <el-button v-if="order.status === 'confirmed'" type="success" size="large" @click="handleComplete">确认交付</el-button>
          <el-button v-if="order.status === 'pending' || order.status === 'confirmed'" type="danger" @click="handleCancel">取消订单</el-button>
        </template>
        <template v-if="isSeller">
          <el-button v-if="order.status === 'pending'" type="primary" size="large" @click="handleConfirm">确认订单</el-button>
          <el-button v-if="order.status === 'pending'" type="danger" @click="handleReject">拒绝订单</el-button>
          <el-button v-if="order.status === 'confirmed'" type="danger" @click="handleCancel">取消订单</el-button>
        </template>
      </div>
      <div v-if="order.status === 'completed' && isBuyer && !hasReviewed" class="action-bar">
        <el-button type="primary" size="large" @click="showReviewDialog = true">评价订单</el-button>
      </div>

      <ReviewDialog v-model="showReviewDialog" :order="order" @success="onReviewSuccess" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { getOrderDetail, confirmOrder, rejectOrder, completeOrder, cancelOrder } from '../../api/order'
import type { OrderDetail } from '../../api/order'
import { getDeviceReviews } from '../../api/review'
import StatusTag from '../../components/StatusTag.vue'
import ReviewDialog from '../review/ReviewDialog.vue'
import { formatPrice, formatDate } from '../../utils/format'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const order = ref<OrderDetail | null>(null)
const showReviewDialog = ref(false)
const hasReviewed = ref(false)

const isBuyer = computed(() => authStore.user?.id === order.value?.buyer_id)
const isSeller = computed(() => authStore.user?.id === order.value?.seller_id)

const stepActive = computed(() => {
  if (!order.value) return 0
  const map: Record<string, number> = { pending: 1, confirmed: 2, completed: 3, cancelled: 0 }
  return map[order.value.status] ?? 0
})

onMounted(async () => {
  try {
    const resp = await getOrderDetail(route.params.id as string)
    order.value = resp.data.data
    await checkReviewed()
  } catch (e: any) { ElMessage.error(e.message || '获取订单失败') }
  finally { loading.value = false }
})

async function checkReviewed() {
  if (!order.value || order.value.status !== 'completed' || !isBuyer.value) return
  try {
    const resp = await getDeviceReviews(order.value.device_id, { page: 1, size: 100 })
    const reviews = resp.data.data.items
    hasReviewed.value = reviews.some((r: any) => r.order_id === order.value!.id)
  } catch { /* ignore */ }
}

function onReviewSuccess() {
  hasReviewed.value = true
}

async function handleConfirm() {
  try { await confirmOrder(order.value!.id); ElMessage.success('已确认'); refresh() } catch (e: any) { ElMessage.error(e.message) }
}

async function handleReject() {
  try { await ElMessageBox.confirm('确定拒绝？', '提示', { type: 'warning' }); await rejectOrder(order.value!.id); ElMessage.success('已拒绝'); refresh() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}

async function handleComplete() {
  try { await ElMessageBox.confirm('确认已收到设备？', '确认交付'); await completeOrder(order.value!.id); ElMessage.success('已确认交付'); refresh() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}

async function handleCancel() {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消订单', { inputPattern: /.+/, inputErrorMessage: '取消原因不能为空' })
    await cancelOrder(order.value!.id, value); ElMessage.success('已取消'); refresh()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.message) }
}

async function refresh() {
  const resp = await getOrderDetail(order.value!.id)
  order.value = resp.data.data
}
</script>

<style scoped>
.order-detail {
  padding: 32px 24px;
  max-width: 800px;
  margin: 0 auto;
  animation: fadeInUp 0.5s ease-out;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.order-no {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 16px;
}

.header-status {
  flex-shrink: 0;
}

.status-steps-wrapper {
  margin: 24px 0 32px;
  padding: 24px;
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.info-card {
  margin-bottom: 16px;
  padding: 24px;
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.card-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
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

.device-info {
  display: flex;
  gap: 16px;
  align-items: center;
  cursor: pointer;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: var(--color-muted);
  transition: var(--transition-normal);
}

.device-info:hover {
  background: var(--color-border);
}

.device-thumb-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.device-thumb {
  width: 72px;
  height: 72px;
}

.thumb-placeholder {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-border);
  color: var(--color-muted-foreground);
  font-size: 12px;
}

.device-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.device-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.device-price {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 12px;
  color: var(--color-muted-foreground);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 14px;
  color: var(--color-foreground);
  font-weight: 500;
}

.info-value.mono {
  font-family: var(--font-mono);
  font-size: 13px;
}

.cancel-reason {
  color: var(--color-danger);
}

.action-bar {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 28px;
  padding: 20px;
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
</style>
