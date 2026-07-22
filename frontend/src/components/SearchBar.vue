<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <el-input
        v-model="keyword"
        placeholder="搜索你想要的设备..."
        clearable
        size="large"
        class="search-input"
        data-testid="input-search"
        @input="onKeywordChange"
        @clear="onSearch"
      >
        <template #prefix>
          <el-icon class="search-icon"><Search /></el-icon>
        </template>
      </el-input>
    </div>
    <div class="filter-row">
      <div class="filter-chip">
        <el-icon class="filter-chip-icon"><Filter /></el-icon>
        <span class="filter-chip-label">筛选</span>
      </div>
      <el-select v-model="conditionLevel" placeholder="成色" clearable class="filter-item" @change="onSearch">
        <el-option label="几乎全新" value="almost_new" />
        <el-option label="成色良好" value="good" />
        <el-option label="一般" value="fair" />
        <el-option label="较差" value="poor" />
      </el-select>
      <div class="price-range">
        <el-input-number v-model="minPrice" :min="0" placeholder="最低价" :controls="false" class="price-input" @change="onSearch" />
        <span class="price-sep">—</span>
        <el-input-number v-model="maxPrice" :min="0" placeholder="最高价" :controls="false" class="price-input" @change="onSearch" />
      </div>
      <el-select v-model="sortField" class="filter-item sort-select" @change="onSearch">
        <el-option label="最新发布" value="created_at" />
        <el-option label="价格最低" value="price_asc" />
        <el-option label="价格最高" value="price_desc" />
      </el-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, Filter } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  initialKeyword?: string
}>(), {
  initialKeyword: '',
})

const emit = defineEmits<{
  search: [filters: {
    keyword: string
    conditionLevel: string
    minPrice: number | null
    maxPrice: number | null
    sort: string
    order: string
  }]
}>()

const keyword = ref(props.initialKeyword)
const conditionLevel = ref('')
const minPrice = ref<number | null>(null)
const maxPrice = ref<number | null>(null)
const sortField = ref('created_at')

watch(() => props.initialKeyword, (val) => {
  if (val !== keyword.value) {
    keyword.value = val
    onSearch()
  }
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onKeywordChange() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(onSearch, 300)
}

function onSearch() {
  let sort = 'created_at'
  let order = 'desc'
  if (sortField.value === 'price_asc') { sort = 'price'; order = 'asc' }
  else if (sortField.value === 'price_desc') { sort = 'price'; order = 'desc' }

  emit('search', {
    keyword: keyword.value,
    conditionLevel: conditionLevel.value,
    minPrice: minPrice.value,
    maxPrice: maxPrice.value,
    sort,
    order,
  })
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 24px;
}

.search-input-wrapper {
  position: relative;
  margin-bottom: 16px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-lg) !important;
  padding: 4px 20px;
  box-shadow: var(--shadow-md) !important;
  border: 2px solid transparent !important;
  transition: var(--transition-normal);
  background: var(--color-card) !important;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: var(--shadow-lg) !important;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-accent) !important;
  box-shadow: var(--shadow-lg), 0 0 0 4px rgba(0, 82, 255, 0.1) !important;
}

.search-input :deep(.el-input__inner) {
  font-size: 15px;
  height: 40px;
}

.search-icon {
  font-size: 18px;
  color: var(--color-muted-foreground);
  transition: var(--transition-normal);
}

.search-input :deep(.el-input__wrapper.is-focus) .search-icon {
  color: var(--color-accent);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-secondary) 100%);
  color: var(--color-accent-foreground);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.filter-chip-icon {
  font-size: 14px;
}

.filter-item {
  width: 140px;
}

.filter-item :deep(.el-input__wrapper) {
  border-radius: 20px !important;
  padding: 2px 14px;
  background: var(--color-card) !important;
  box-shadow: var(--shadow-sm) !important;
  border: 1px solid var(--color-border) !important;
  transition: var(--transition-normal);
}

.filter-item :deep(.el-input__wrapper:hover) {
  border-color: var(--color-accent-secondary) !important;
}

.filter-item :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-accent) !important;
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.1) !important;
}

.sort-select {
  width: 130px;
}

.price-range {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  background: var(--color-card);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: var(--transition-normal);
}

.price-range:focus-within {
  border-color: var(--color-accent-secondary);
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.1);
}

.price-input {
  width: 90px;
}

.price-input :deep(.el-input__wrapper) {
  border-radius: 10px !important;
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
  padding: 0 4px;
}

.price-input :deep(.el-input__inner) {
  font-size: 13px;
  text-align: center;
}

.price-sep {
  color: var(--color-muted-foreground);
  font-size: 13px;
  font-weight: 500;
}
</style>