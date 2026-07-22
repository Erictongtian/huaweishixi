<template>
  <div v-loading="loading" class="device-detail">
    <template v-if="device">
      <div class="back-bar">
        <el-button text @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
      </div>
      <div class="detail-layout">
        <div class="detail-images">
          <div class="main-image-wrapper">
            <el-image :src="currentImage" fit="contain" class="main-image" :preview-src-list="imageUrls" />
          </div>
          <div v-if="device.images.length > 1" class="thumbnail-list">
            <div
              v-for="(img, idx) in device.images"
              :key="img.id"
              class="thumbnail"
              :class="{ active: currentImageIdx === idx }"
              @click="currentImageIdx = idx"
            >
              <el-image :src="img.url" fit="cover" />
            </div>
          </div>
        </div>
        <div class="detail-info">
          <div class="detail-status-bar">
            <el-tag
              :type="device.status === 'on_sale' ? 'success' : device.status === 'sold' ? 'info' : 'warning'"
              effect="dark"
              round
              class="status-tag"
            >
              {{ deviceStatusMap[device.status] }}
            </el-tag>
            <span class="view-count">
              <el-icon><View /></el-icon>
              {{ device.view_count }} 次浏览
            </span>
          </div>
          <h1 class="detail-title">{{ device.title }}</h1>
          <div class="detail-price">
            <span class="price">{{ formatPrice(parseFloat(device.price)) }}</span>
            <span v-if="device.original_price" class="original-price">
              {{ formatPrice(parseFloat(device.original_price)) }}
            </span>
            <span v-if="device.original_price" class="discount-badge">
              {{ Math.round((1 - parseFloat(device.price) / parseFloat(device.original_price)) * 100) }}% OFF
            </span>
          </div>
          <div class="detail-attrs-grid">
            <div class="attr-item">
              <span class="attr-label">分类</span>
              <span class="attr-value">{{ device.category?.name || '-' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">成色</span>
              <span class="attr-value">{{ conditionLevelMap[device.condition_level] || device.condition_level }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">使用时间</span>
              <span class="attr-value">{{ device.usage_duration || '-' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">位置</span>
              <span class="attr-value">{{ device.location || '-' }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">联系方式</span>
              <span class="attr-value">{{ device.contact_info || '-' }}</span>
            </div>
          </div>
          <div class="seller-card">
            <el-avatar :size="40" class="seller-avatar">{{ device.seller?.nickname?.charAt(0) }}</el-avatar>
            <div class="seller-meta">
              <span class="seller-name">{{ device.seller?.nickname }}</span>
              <span class="seller-label">卖家</span>
            </div>
          </div>
          <div class="detail-actions">
            <template v-if="isOwner">
              <el-button type="primary" @click="$router.push(`/devices/publish?edit=${device.id}`)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button v-if="device.status === 'on_sale'" type="warning" @click="handleOffShelf">
                <el-icon><Bottom /></el-icon> 下架
              </el-button>
              <el-button v-if="device.status === 'off_shelf'" type="success" @click="handleOnShelf">
                <el-icon><Top /></el-icon> 上架
              </el-button>
            </template>
            <template v-else-if="device.status === 'on_sale'">
              <el-button type="primary" size="large" class="buy-btn" @click="showBuyDialog = true">
                <el-icon><ShoppingCart /></el-icon> 立即购买
              </el-button>
            </template>
          </div>
        </div>
      </div>
      <div v-if="device.description" class="detail-description">
        <h3>设备描述</h3>
        <p>{{ device.description }}</p>
      </div>

      <div class="detail-reviews">
        <div class="reviews-header">
          <h3>用户评价</h3>
          <span v-if="reviewTotal > 0" class="review-summary">
            <el-icon style="color: #f59e0b; vertical-align: middle;"><StarFilled /></el-icon>
            {{ reviewAvg }}
            <span class="review-count">（{{ reviewTotal }}条评价）</span>
          </span>
        </div>
        <div v-if="reviews.length === 0" class="no-reviews">暂无评价</div>
        <div v-for="review in reviews" :key="review.id" class="review-item">
          <div class="review-user">
            <el-avatar :size="36" class="reviewer-avatar">{{ review.reviewer_nickname?.charAt(0) || '?' }}</el-avatar>
            <div class="review-user-info">
              <span class="review-nickname">{{ review.reviewer_nickname || '匿名用户' }}</span>
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
            </div>
          </div>
          <div class="review-stars">
            <el-icon v-for="s in 5" :key="s" :style="{ color: s <= review.rating ? '#f59e0b' : '#d1d5db' }"><StarFilled /></el-icon>
          </div>
          <p v-if="review.content" class="review-content">{{ review.content }}</p>
          <div v-if="review.images?.length" class="review-images">
            <el-image v-for="(img, idx) in review.images" :key="idx" :src="img" fit="cover" class="review-img"
              :preview-src-list="review.images" :initial-index="idx" />
          </div>
        </div>
        <el-button v-if="reviewPage < reviewPages" text type="primary" @click="loadMoreReviews">查看更多评价</el-button>
      </div>
    </template>

    <el-dialog v-model="showBuyDialog" title="确认购买" width="440px" class="buy-dialog">
      <div class="buy-dialog-body">
        <p class="buy-device-name">确定购买「{{ device?.title }}」？</p>
        <p class="buy-price">{{ device ? formatPrice(parseFloat(device.price)) : '' }}</p>
        <el-input v-model="buyerMessage" type="textarea" :rows="3" placeholder="给卖家留言（选填）" />
      </div>
      <template #footer>
        <el-button @click="showBuyDialog = false">取消</el-button>
        <el-button type="primary" :loading="buying" @click="handleBuy">确认购买</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StarFilled, View, Edit, Bottom, Top, ShoppingCart, ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { getDeviceDetail, toggleStatus } from '../../api/device'
import { createOrder } from '../../api/order'
import { getDeviceReviews } from '../../api/review'
import type { DeviceDetail } from '../../api/device'
import type { ReviewItem } from '../../api/review'
import { formatPrice, formatDate, conditionLevelMap, deviceStatusMap } from '../../utils/format'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const device = ref<DeviceDetail | null>(null)
const currentImageIdx = ref(0)
const showBuyDialog = ref(false)
const buyerMessage = ref('')
const buying = ref(false)
const router = useRouter()

const reviews = ref<ReviewItem[]>([])
const reviewTotal = ref(0)
const reviewAvg = ref('0.0')
const reviewPage = ref(1)
const reviewPages = ref(0)

const currentImage = computed(() => {
  if (!device.value?.images?.length) return ''
  return device.value.images[currentImageIdx.value]?.url || ''
})

const imageUrls = computed(() => device.value?.images?.map((i) => i.url) || [])

const isOwner = computed(() => authStore.user?.id === device.value?.seller_id)

onMounted(async () => {
  try {
    const resp = await getDeviceDetail(route.params.id as string)
    device.value = resp.data.data
    await loadReviews()
  } catch (e: any) {
    ElMessage.error(e.message || '获取设备详情失败')
  } finally {
    loading.value = false
  }
})

async function loadReviews() {
  try {
    const deviceId = route.params.id as string
    const resp = await getDeviceReviews(deviceId, { page: reviewPage.value, size: 5 })
    const d = resp.data.data
    if (reviewPage.value === 1) {
      reviews.value = d.items
    } else {
      reviews.value.push(...d.items)
    }
    reviewTotal.value = d.total
    reviewPages.value = d.pages
    if (d.total > 0) {
      const sum = reviews.value.reduce((acc, r) => acc + r.rating, 0)
      reviewAvg.value = (sum / reviews.value.length).toFixed(1)
    }
  } catch { /* ignore */ }
}

async function loadMoreReviews() {
  reviewPage.value++
  await loadReviews()
}

async function handleOffShelf() {
  try {
    await ElMessageBox.confirm('确定下架该设备？', '提示', { type: 'warning' })
    await toggleStatus(device.value!.id, 'off_shelf')
    device.value!.status = 'off_shelf'
    ElMessage.success('已下架')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '下架失败')
  }
}

async function handleOnShelf() {
  try {
    await toggleStatus(device.value!.id, 'on_sale')
    device.value!.status = 'on_sale'
    ElMessage.success('已上架')
  } catch (e: any) {
    ElMessage.error(e.message || '上架失败')
  }
}

async function handleBuy() {
  buying.value = true
  try {
    await createOrder({ device_id: device.value!.id, buyer_message: buyerMessage.value || undefined })
    ElMessage.success('下单成功')
    showBuyDialog.value = false
    router.push('/orders')
  } catch (e: any) {
    ElMessage.error(e.message || '购买失败')
  } finally {
    buying.value = false
  }
}
</script>

<style scoped>
.device-detail {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
  animation: fadeInUp 0.5s ease-out;
}

.back-bar {
  margin-bottom: 16px;
}

.back-bar :deep(.el-button) {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-muted-foreground);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: var(--transition-normal);
}

.back-bar :deep(.el-button:hover) {
  color: var(--color-accent);
  background: var(--color-muted);
}

.detail-layout {
  display: flex;
  gap: 40px;
  margin-bottom: 32px;
}

.detail-images {
  width: 44%;
  flex-shrink: 0;
}

.main-image-wrapper {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: var(--color-muted);
}

.main-image {
  width: 100%;
  height: 380px;
  border-radius: var(--radius-lg);
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.thumbnail {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  border: 2px solid var(--color-border);
  transition: var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.thumbnail:hover {
  border-color: var(--color-accent-secondary);
  transform: translateY(-2px);
}

.thumbnail.active {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.2);
}

.detail-info {
  flex: 1;
}

.detail-status-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.status-tag {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.view-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-muted-foreground);
}

.detail-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 16px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.detail-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.price {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.original-price {
  font-size: 16px;
  color: var(--color-muted-foreground);
  text-decoration: line-through;
}

.discount-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  color: white;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: 0.02em;
}

.detail-attrs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.attr-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  border: 1px solid var(--color-border);
}

.attr-label {
  font-size: 12px;
  color: var(--color-muted-foreground);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.attr-value {
  font-size: 14px;
  color: var(--color-foreground);
  font-weight: 600;
  font-family: var(--font-display);
}

.seller-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: var(--radius-md);
  background: var(--color-card);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
  transition: var(--transition-normal);
}

.seller-card:hover {
  box-shadow: var(--shadow-md);
}

.seller-avatar {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  font-family: var(--font-display);
  font-weight: 700;
}

.seller-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.seller-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.seller-label {
  font-size: 12px;
  color: var(--color-muted-foreground);
}

.detail-actions {
  margin-top: 8px;
  display: flex;
  gap: 12px;
}

.buy-btn {
  min-width: 180px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-display);
  border-radius: var(--radius-md) !important;
  letter-spacing: 0.02em;
}

.detail-description {
  margin-top: 32px;
  padding: 28px;
  border-radius: var(--radius-lg);
  background: var(--color-card);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.detail-description h3 {
  font-size: 18px;
  margin: 0 0 12px;
  font-family: var(--font-display);
  color: var(--color-foreground);
}

.detail-description p {
  color: var(--color-muted-foreground);
  line-height: 1.8;
  white-space: pre-wrap;
  font-size: 15px;
}

.buy-dialog-body {
  text-align: center;
}

.buy-device-name {
  font-size: 16px;
  color: var(--color-foreground);
  margin: 0 0 8px;
}

.buy-price {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 8px 0 16px;
  font-family: var(--font-display);
}

.detail-reviews {
  margin-top: 32px;
  padding: 28px;
  border-radius: var(--radius-lg);
  background: var(--color-card);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.reviews-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.reviews-header h3 {
  font-size: 18px;
  margin: 0;
  font-family: var(--font-display);
}

.review-summary {
  font-size: 15px;
  color: var(--color-muted-foreground);
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.review-count {
  color: var(--color-muted-foreground);
  font-size: 13px;
  font-weight: 400;
}

.no-reviews {
  color: var(--color-muted-foreground);
  font-size: 14px;
  padding: 40px 0;
  text-align: center;
}

.review-item {
  padding: 20px 0;
  border-bottom: 1px solid var(--color-border);
}

.review-item:last-child {
  border-bottom: none;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.reviewer-avatar {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  font-family: var(--font-display);
  font-weight: 700;
}

.review-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.review-nickname {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.review-date {
  font-size: 12px;
  color: var(--color-muted-foreground);
}

.review-stars {
  display: flex;
  gap: 2px;
  margin-bottom: 8px;
}

.review-content {
  font-size: 14px;
  color: var(--color-muted-foreground);
  line-height: 1.7;
  margin: 0 0 10px;
}

.review-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.review-img {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-normal);
}

.review-img:hover {
  transform: scale(1.05);
}
</style>
