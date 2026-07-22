<template>
  <el-tag :type="tagType" size="small" effect="dark" round class="status-tag">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { deviceStatusMap, orderStatusMap } from '../utils/format'

const props = defineProps<{ status: string; type?: 'device' | 'order' }>()

const label = computed(() => {
  if (props.type === 'device') return deviceStatusMap[props.status] || props.status
  return orderStatusMap[props.status] || props.status
})

const tagType = computed(() => {
  const map: Record<string, string> = {
    on_sale: 'success',
    off_shelf: 'warning',
    sold: 'info',
    pending: 'warning',
    confirmed: '',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[props.status] || 'info'
})
</script>

<style scoped>
.status-tag {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.02em;
}
</style>