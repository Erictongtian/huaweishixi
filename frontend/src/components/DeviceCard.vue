<template>
  <div class="device-card" @click="$router.push(`/devices/${device.id}`)">
    <div class="card-image">
      <el-image :src="device.image_url || '/placeholder.png'" fit="cover" class="image" />
      <div class="image-overlay" />
      <el-tag v-if="device.condition_level" class="condition-tag" size="small" :type="conditionType" effect="dark">
        {{ conditionLabel }}
      </el-tag>
      <StatusTag v-if="device.status !== 'on_sale'" :status="device.status" type="device" class="status-tag" />
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ device.title }}</h3>
      <div class="card-price">
        <span class="price">{{ formatPrice(parseFloat(device.price)) }}</span>
        <span v-if="device.original_price" class="original-price">
          {{ formatPrice(parseFloat(device.original_price)) }}
        </span>
      </div>
      <div class="card-meta">
        <span v-if="device.location" class="meta-item">
          <el-icon :size="12"><Location /></el-icon>{{ device.location }}
        </span>
        <span v-if="device.seller_nickname" class="meta-item">
          <el-icon :size="12"><User /></el-icon>{{ device.seller_nickname }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Location, User } from '@element-plus/icons-vue'
import type { DeviceListItem } from '../api/device'
import { formatPrice, conditionLevelMap } from '../utils/format'
import StatusTag from './StatusTag.vue'

const props = defineProps<{ device: DeviceListItem }>()

const conditionLabel = computed(() => conditionLevelMap[props.device.condition_level] || props.device.condition_level)

const conditionType = computed(() => {
  const map: Record<string, string> = { almost_new: 'success', good: '', fair: 'warning', poor: 'danger' }
  return map[props.device.condition_level] || ''
})
</script>

<style scoped>
.device-card {
  cursor: pointer;
  background: var(--color-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: var(--transition-slow);
  box-shadow: var(--shadow-sm);
}
.device-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(0, 82, 255, 0.2);
}
.card-image {
  position: relative;
  width: 100%;
  padding-top: 75%;
  overflow: hidden;
}
.image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: transform 0.4s ease;
}
.device-card:hover .image {
  transform: scale(1.05);
}
.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.15), transparent);
  pointer-events: none;
}
.condition-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  border-radius: 6px;
  font-size: 11px;
  backdrop-filter: blur(4px);
}
.status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}
.card-body {
  padding: 14px 16px 16px;
}
.card-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--color-foreground);
  margin: 0 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.card-price {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.price {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.original-price {
  font-size: 13px;
  color: var(--color-muted-foreground);
  text-decoration: line-through;
}
.card-meta {
  display: flex;
  gap: 14px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--color-muted-foreground);
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
}
</style>
