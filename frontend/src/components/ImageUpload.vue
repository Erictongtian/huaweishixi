<template>
  <div class="image-upload">
    <div class="image-list">
      <div v-for="(img, index) in imageList" :key="img.id || index" class="image-item">
        <el-image :src="img.url" fit="cover" class="image-preview" />
        <div class="image-overlay">
          <div class="image-actions">
            <el-icon v-if="index > 0" @click.stop="moveImage(index, -1)"><ArrowLeft /></el-icon>
            <el-icon @click.stop="removeImage(index)"><Delete /></el-icon>
            <el-icon v-if="index < imageList.length - 1" @click.stop="moveImage(index, 1)"><ArrowRight /></el-icon>
          </div>
        </div>
        <div v-if="index === 0" class="cover-badge">封面</div>
      </div>
      <div v-if="imageList.length < maxCount" class="upload-trigger" @click="triggerUpload">
        <el-icon :size="28"><Plus /></el-icon>
        <span>上传图片</span>
        <span class="upload-count">{{ imageList.length }}/{{ maxCount }}</span>
      </div>
    </div>
    <input ref="fileInput" type="file" :accept="accept" multiple class="hidden-input" @change="onFileChange" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export interface ImageItem {
  id?: string
  url: string
  file?: File
}

const props = withDefaults(defineProps<{
  modelValue: ImageItem[]
  maxCount?: number
  maxSize?: number
  accept?: string
}>(), {
  maxCount: 5,
  maxSize: 5 * 1024 * 1024,
  accept: 'image/jpeg,image/png,image/gif,image/webp',
})

const emit = defineEmits<{ 'update:modelValue': [value: ImageItem[]] }>()

const fileInput = ref<HTMLInputElement>()
const imageList = ref<ImageItem[]>([...props.modelValue])

watch(() => props.modelValue, (val) => { imageList.value = [...val] })

function triggerUpload() {
  fileInput.value?.click()
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  const files = Array.from(input.files)
  const remaining = props.maxCount - imageList.value.length
  const toAdd = files.slice(0, remaining)

  for (const file of toAdd) {
    if (file.size > props.maxSize) {
      ElMessage.warning(`${file.name} 超过5MB限制`)
      continue
    }
    if (!props.accept.split(',').includes(file.type)) {
      ElMessage.warning(`${file.name} 格式不支持`)
      continue
    }
    const url = URL.createObjectURL(file)
    imageList.value.push({ url, file })
  }
  input.value = ''
  emit('update:modelValue', [...imageList.value])
}

function removeImage(index: number) {
  imageList.value.splice(index, 1)
  emit('update:modelValue', [...imageList.value])
}

function moveImage(index: number, direction: number) {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= imageList.value.length) return
  const temp = imageList.value[index]
  imageList.value[index] = imageList.value[newIndex]
  imageList.value[newIndex] = temp
  emit('update:modelValue', [...imageList.value])
}
</script>

<style scoped>
.image-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.image-item {
  position: relative;
  width: 110px;
  height: 110px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 2px solid var(--color-border);
  transition: var(--transition-normal);
}

.image-item:hover {
  border-color: var(--color-accent-secondary);
  box-shadow: var(--shadow-md);
}

.image-preview {
  width: 100%;
  height: 100%;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: var(--transition-normal);
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  gap: 12px;
  color: white;
  font-size: 18px;
}

.image-actions .el-icon {
  cursor: pointer;
  transition: var(--transition-fast);
}

.image-actions .el-icon:hover {
  transform: scale(1.2);
}

.cover-badge {
  position: absolute;
  top: 4px;
  left: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: white;
  font-size: 10px;
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: 0.05em;
}

.upload-trigger {
  width: 110px;
  height: 110px;
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
  background: var(--color-muted);
}

.upload-trigger:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(0, 82, 255, 0.04);
}

.upload-count {
  font-size: 11px;
  color: var(--color-muted-foreground);
  font-family: var(--font-mono);
}

.hidden-input {
  display: none;
}
</style>