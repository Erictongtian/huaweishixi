<template>
  <div class="device-list-page">
    <div class="page-hero">
      <h1 class="hero-title">发现好物</h1>
      <p class="hero-subtitle">校园二手设备，物尽其用</p>
    </div>

    <div class="category-bar">
      <div
        class="category-chip"
        :class="{ active: activeCategory === '' }"
        @click="selectCategory('')"
      >
        全部
      </div>
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="category-chip"
        :class="{ active: activeCategory === cat.id }"
        @click="selectCategory(cat.id)"
      >
        {{ cat.name }}
        <span v-if="cat.device_count" class="chip-count">{{ cat.device_count }}</span>
      </div>
    </div>

    <SearchBar :initial-keyword="routeKeyword" @search="onSearch" />

    <div v-loading="deviceStore.loading" class="device-grid">
      <DeviceCard v-for="device in deviceStore.devices" :key="device.id" :device="device" />
      <el-empty v-if="!deviceStore.loading && deviceStore.devices.length === 0" description="暂无设备" />
    </div>

    <div v-if="deviceStore.pages > 1" class="pagination">
      <el-pagination
        v-model:current-page="deviceStore.page"
        :page-size="deviceStore.size"
        :total="deviceStore.total"
        layout="prev, pager, next"
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDeviceStore } from '../../stores/device'
import { getCategories } from '../../api/category'
import type { CategoryItem } from '../../api/category'
import DeviceCard from '../../components/DeviceCard.vue'
import SearchBar from '../../components/SearchBar.vue'

const route = useRoute()
const deviceStore = useDeviceStore()
const categories = ref<CategoryItem[]>([])
const activeCategory = ref('')
const routeKeyword = ref((route.query.keyword as string) || '')

onMounted(async () => {
  try {
    const resp = await getCategories()
    categories.value = resp.data.data || []
  } catch {
    categories.value = []
  }
  const kw = route.query.keyword as string
  if (kw) {
    routeKeyword.value = kw
    deviceStore.setFilters({ keyword: kw })
  } else {
    routeKeyword.value = ''
    deviceStore.setFilters({ keyword: '', conditionLevel: '', minPrice: null, maxPrice: null, category: '', sort: 'created_at', order: 'desc' })
    activeCategory.value = ''
  }
  await deviceStore.fetchDevices()
})

watch(() => route.query.keyword, (kw) => {
  if (kw && typeof kw === 'string') {
    routeKeyword.value = kw
    deviceStore.setFilters({ keyword: kw })
  } else {
    routeKeyword.value = ''
    deviceStore.setFilters({ keyword: '' })
  }
  deviceStore.fetchDevices()
})

function selectCategory(catId: string) {
  activeCategory.value = catId
  deviceStore.setFilters({ category: catId || undefined })
  deviceStore.fetchDevices()
}

function onSearch(filters: {
  keyword: string
  conditionLevel: string
  minPrice: number | null
  maxPrice: number | null
  sort: string
  order: string
}) {
  deviceStore.setFilters(filters)
  deviceStore.fetchDevices()
}

function onPageChange(page: number) {
  deviceStore.setPage(page)
  deviceStore.fetchDevices()
}
</script>

<style scoped>
.device-list-page {
  padding: 0;
}
.page-hero {
  text-align: center;
  padding: 32px 0 24px;
  position: relative;
}
.page-hero::before {
  content: '';
  position: absolute;
  top: -32px;
  left: -100px;
  width: 300px;
  height: 200px;
  background: radial-gradient(circle, rgba(0, 82, 255, 0.06) 0%, transparent 70%);
  pointer-events: none;
}
.page-hero::after {
  content: '';
  position: absolute;
  top: -20px;
  right: -80px;
  width: 250px;
  height: 180px;
  background: radial-gradient(circle, rgba(77, 124, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
}
.hero-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
  letter-spacing: -0.03em;
}
.hero-subtitle {
  font-size: 15px;
  color: var(--color-muted-foreground);
  margin: 0;
}
.category-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  color: var(--color-muted-foreground);
  transition: var(--transition-normal);
  user-select: none;
}
.category-chip:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(0, 82, 255, 0.04);
}
.category-chip.active {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: var(--shadow-accent);
}
.chip-count {
  font-size: 11px;
  opacity: 0.7;
  font-family: var(--font-mono);
}
.device-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  min-height: 200px;
}
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 16px;
}

@media (max-width: 1024px) {
  .device-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 768px) {
  .device-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
