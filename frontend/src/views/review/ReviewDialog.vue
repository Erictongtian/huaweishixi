<template>
  <el-dialog v-model="visible" title="评价订单" width="560px" @close="handleClose">
    <div v-if="orderInfo" class="review-device-info">
      <div class="review-thumb-wrapper">
        <el-image :src="orderInfo.device?.image_url || ''" fit="cover" class="review-thumb">
          <template #error><div class="thumb-placeholder">无图</div></template>
        </el-image>
      </div>
      <div class="review-device-meta">
        <div class="review-device-title">{{ orderInfo.device?.title || '设备' }}</div>
        <div class="review-device-price">{{ formatPrice(parseFloat(orderInfo.price)) }}</div>
      </div>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="评分" prop="rating">
        <div class="star-rating">
          <el-icon
            v-for="star in 5"
            :key="star"
            :size="32"
            :class="{ active: star <= hoverRating || (hoverRating === 0 && star <= form.rating) }"
            @mouseenter="hoverRating = star"
            @mouseleave="hoverRating = 0"
            @click="form.rating = star"
          >
            <StarFilled />
          </el-icon>
          <span class="rating-text">{{ form.rating }}分</span>
        </div>
      </el-form-item>

      <el-form-item label="评价内容" prop="content">
        <el-input v-model="form.content" type="textarea" :rows="4" placeholder="分享你的使用感受..." maxlength="500" show-word-limit size="large" />
      </el-form-item>

      <el-form-item label="上传图片（最多3张）">
        <div class="review-images">
          <div v-for="(img, idx) in imageUrls" :key="idx" class="review-img-item">
            <el-image :src="img" fit="cover" />
            <div class="img-overlay">
              <el-icon class="remove-btn" @click="removeImage(idx)"><Close /></el-icon>
            </div>
          </div>
          <div v-if="imageUrls.length < 3" class="upload-trigger" @click="triggerUpload">
            <el-icon :size="24"><Plus /></el-icon>
          </div>
        </div>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/gif,image/webp" class="hidden-input" @change="onFileChange" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">提交评价</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { StarFilled, Plus, Close } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { createReview, uploadFile } from '../../api/review'
import type { ReviewCreate } from '../../api/review'
import type { OrderDetail } from '../../api/order'
import { formatPrice } from '../../utils/format'

const props = defineProps<{
  order: OrderDetail | null
}>()

const emit = defineEmits<{ success: [] }>()

const visible = defineModel<boolean>({ default: false })

const formRef = ref<FormInstance>()
const fileInput = ref<HTMLInputElement>()
const hoverRating = ref(0)
const submitting = ref(false)
const imageUrls = ref<string[]>([])
const uploadingImages = ref(false)

const orderInfo = computed(() => props.order)

const form = reactive<ReviewCreate & { content: string }>({
  order_id: '',
  rating: 5,
  content: '',
  images: [],
})

const rules: FormRules = {
  rating: [{ required: true, message: '请选择评分', trigger: 'change' }],
}

function handleClose() {
  form.order_id = ''
  form.rating = 5
  form.content = ''
  form.images = []
  imageUrls.value = []
  hoverRating.value = 0
  formRef.value?.resetFields()
  visible.value = false
}

function triggerUpload() {
  fileInput.value?.click()
}

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片不能超过5MB')
    input.value = ''
    return
  }
  uploadingImages.value = true
  try {
    const resp = await uploadFile(file)
    const url = resp.data.data.url
    imageUrls.value.push(url)
    form.images = [...imageUrls.value]
  } catch (err: any) {
    ElMessage.error(err.message || '上传失败')
  } finally {
    uploadingImages.value = false
    input.value = ''
  }
}

function removeImage(idx: number) {
  imageUrls.value.splice(idx, 1)
  form.images = [...imageUrls.value]
}

async function handleSubmit() {
  if (!props.order) return
  if (form.rating === 0) {
    ElMessage.warning('请选择评分')
    return
  }
  form.order_id = props.order.id
  if (form.images && form.images.length === 0) {
    delete form.images
  }
  submitting.value = true
  try {
    await createReview({ ...form, images: form.images?.length ? form.images : undefined })
    ElMessage.success('评价成功')
    emit('success')
    handleClose()
  } catch (err: any) {
    ElMessage.error(err.message || '评价失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-device-info {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  background: var(--color-muted);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-bottom: 24px;
}

.review-thumb-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.review-thumb {
  width: 56px;
  height: 56px;
}

.thumb-placeholder {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-border);
  color: var(--color-muted-foreground);
  font-size: 12px;
}

.review-device-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.review-device-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.review-device-price {
  font-size: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.star-rating {
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-rating .el-icon {
  color: var(--color-border);
  cursor: pointer;
  transition: var(--transition-fast);
}

.star-rating .el-icon:hover {
  transform: scale(1.2);
}

.star-rating .el-icon.active {
  color: #f59e0b;
}

.rating-text {
  margin-left: 8px;
  font-size: 15px;
  color: var(--color-muted-foreground);
  font-weight: 600;
  font-family: var(--font-display);
}

.review-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.review-img-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.review-img-item .el-image {
  width: 100%;
  height: 100%;
}

.img-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: var(--transition-normal);
}

.review-img-item:hover .img-overlay {
  opacity: 1;
}

.remove-btn {
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.remove-btn:hover {
  transform: scale(1.2);
}

.upload-trigger {
  width: 80px;
  height: 80px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-muted-foreground);
  transition: var(--transition-normal);
  background: var(--color-muted);
}

.upload-trigger:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(0, 82, 255, 0.04);
}

.hidden-input {
  display: none;
}
</style>