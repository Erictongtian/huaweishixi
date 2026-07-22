<template>
  <div class="device-publish">
    <div class="page-header">
      <h2 class="page-title">{{ isEdit ? '编辑设备' : '发布设备' }}</h2>
      <p class="page-subtitle">{{ isEdit ? '修改你的设备信息' : '分享你的闲置设备，让它找到新主人' }}</p>
    </div>
    <div class="publish-form-wrapper">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="publish-form" v-loading="loading">
        <div class="form-section">
          <div class="section-header">
            <div class="section-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="2" y="2" width="16" height="16" rx="4" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="7" cy="7" r="1.5" fill="currentColor"/>
                <path d="M2 14L7 9L10 12L13 9L18 14" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="section-title">基本信息</span>
          </div>
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" placeholder="请输入设备标题" maxlength="100" show-word-limit size="large" />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="分类" prop="category_id" class="form-row-item">
              <el-select v-model="form.category_id" placeholder="请选择分类" size="large">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="成色" prop="condition_level" class="form-row-item">
              <el-select v-model="form.condition_level" placeholder="请选择成色" size="large">
                <el-option label="几乎全新" value="almost_new" />
                <el-option label="成色良好" value="good" />
                <el-option label="一般" value="fair" />
                <el-option label="较差" value="poor" />
              </el-select>
            </el-form-item>
          </div>
          <div class="form-row">
            <el-form-item label="价格" prop="price" class="form-row-item">
              <el-input-number v-model="form.price" :min="0.01" :max="99999.99" :precision="2" :step="10" size="large" class="full-width" />
            </el-form-item>
            <el-form-item label="原价" class="form-row-item">
              <el-input-number v-model="form.original_price" :min="0.01" :max="99999.99" :precision="2" :step="10" size="large" class="full-width" />
            </el-form-item>
          </div>
          <div class="form-row">
            <el-form-item label="使用时间" class="form-row-item">
              <el-input v-model="form.usage_duration" placeholder="如：6个月" size="large" />
            </el-form-item>
            <el-form-item label="位置" class="form-row-item">
              <el-input v-model="form.location" placeholder="如：东区宿舍" size="large" />
            </el-form-item>
          </div>
          <el-form-item label="联系方式" prop="contact_info">
            <el-input v-model="form.contact_info" placeholder="手机号或微信" size="large" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-header">
            <div class="section-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 4H16V16H4V4Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                <path d="M4 8H16" stroke="currentColor" stroke-width="1.5"/>
                <path d="M8 8V16" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
            <span class="section-title">设备描述</span>
          </div>
          <el-form-item label="描述" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请描述设备详情，包括品牌、型号、购买时间、使用情况等" size="large" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-header">
            <div class="section-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="3" y="3" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M10 7V3M10 17V13M13 10H17M3 10H7" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
            <span class="section-title">设备照片</span>
          </div>
          <el-form-item label="照片">
            <ImageUpload v-model="images" :max-count="5" />
          </el-form-item>
        </div>

        <div class="form-actions">
          <el-button @click="$router.back()" size="large">取消</el-button>
          <el-button type="primary" :loading="submitting" size="large" class="submit-btn" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '发布设备' }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getCategories } from '../../api/category'
import type { CategoryItem } from '../../api/category'
import { publishDevice, getDeviceDetail, updateDevice, uploadDeviceImage, deleteDeviceImage, reorderDeviceImages } from '../../api/device'
import ImageUpload from '../../components/ImageUpload.vue'
import type { ImageItem } from '../../components/ImageUpload.vue'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const categories = ref<CategoryItem[]>([])
const images = ref<ImageItem[]>([])
const originalImageIds = ref<string[]>([])

const isEdit = computed(() => !!route.query.edit)
const editId = computed(() => route.query.edit as string)

const form = reactive({
  title: '',
  category_id: '',
  price: 0.01,
  original_price: undefined as number | undefined,
  condition_level: '',
  usage_duration: '',
  location: '',
  contact_info: '',
  description: '',
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  condition_level: [{ required: true, message: '请选择成色', trigger: 'change' }],
  contact_info: [{ required: true, message: '请输入联系方式', trigger: 'blur' }],
  description: [{ required: true, message: '请输入设备描述', trigger: 'blur' }],
}

onMounted(async () => {
  try {
    const resp = await getCategories()
    categories.value = resp.data.data || []
  } catch { categories.value = [] }

  if (isEdit.value) {
    loading.value = true
    try {
      const resp = await getDeviceDetail(editId.value)
      const d = resp.data.data
      form.title = d.title
      form.category_id = d.category_id
      form.price = parseFloat(d.price)
      form.original_price = d.original_price ? parseFloat(d.original_price) : undefined
      form.condition_level = d.condition_level
      form.usage_duration = d.usage_duration || ''
      form.location = d.location || ''
      form.contact_info = d.contact_info || ''
      form.description = d.description || ''
      images.value = (d.images || []).map((img: any) => ({ id: img.id, url: img.url }))
      originalImageIds.value = (d.images || []).map((img: any) => img.id)
    } catch (e: any) {
      ElMessage.error(e.message || '获取设备信息失败')
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  if (images.value.length === 0) {
    ElMessage.warning('请至少上传一张设备照片')
    return
  }

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateDevice(editId.value, {
        title: form.title,
        description: form.description,
        usage_duration: form.usage_duration,
        condition_level: form.condition_level,
        location: form.location,
        contact_info: form.contact_info,
      })

      const currentImageIds = images.value.filter(img => img.id).map(img => img.id!)
      const deletedIds = originalImageIds.value.filter(id => !currentImageIds.includes(id))
      for (const imageId of deletedIds) {
        await deleteDeviceImage(editId.value, imageId)
      }

      for (const img of images.value) {
        if (img.file) {
          await uploadDeviceImage(editId.value, img.file)
        }
      }

      const finalImageIds = images.value.filter(img => img.id).map(img => img.id!)
      if (finalImageIds.length > 0) {
        await reorderDeviceImages(editId.value, finalImageIds)
      }

      ElMessage.success('修改成功')
    } else {
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('category_id', form.category_id)
      formData.append('price', form.price.toString())
      formData.append('condition_level', form.condition_level)
      formData.append('description', form.description)
      formData.append('contact_info', form.contact_info)
      if (form.original_price) formData.append('original_price', form.original_price.toString())
      if (form.usage_duration) formData.append('usage_duration', form.usage_duration)
      if (form.location) formData.append('location', form.location)

      for (const img of images.value) {
        if (img.file) formData.append('images', img.file)
      }
      await publishDevice(formData)
      ElMessage.success('发布成功')
    }
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.device-publish {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 24px;
  animation: fadeInUp 0.5s ease-out;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-muted-foreground);
  margin: 0;
}

.publish-form-wrapper {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.publish-form {
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.section-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-foreground);
  font-family: var(--font-display);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row-item {
  flex: 1;
}

.full-width {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
}

.submit-btn {
  min-width: 140px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  font-family: var(--font-display);
  border-radius: var(--radius-md) !important;
}
</style>
