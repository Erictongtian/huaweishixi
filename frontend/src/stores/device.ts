import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDeviceList } from '../api/device'
import type { DeviceListItem, DeviceListParams } from '../api/device'

export const useDeviceStore = defineStore('device', () => {
  const devices = ref<DeviceListItem[]>([])
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const filters = ref({
    keyword: '',
    category: '',
    conditionLevel: '',
    minPrice: null as number | null,
    maxPrice: null as number | null,
    sort: 'created_at',
    order: 'desc',
  })

  async function fetchDevices() {
    loading.value = true
    try {
      const params: DeviceListParams = {
        page: page.value,
        size: size.value,
        sort: filters.value.sort,
        order: filters.value.order,
      }
      if (filters.value.keyword) params.keyword = filters.value.keyword
      if (filters.value.category) params.category = filters.value.category
      if (filters.value.conditionLevel) params.condition_level = filters.value.conditionLevel
      if (filters.value.minPrice !== null) params.min_price = filters.value.minPrice
      if (filters.value.maxPrice !== null) params.max_price = filters.value.maxPrice

      const resp = await getDeviceList(params)
      const res = resp.data.data
      devices.value = res.items || []
      total.value = res.total || 0
      pages.value = res.pages || 0
    } finally {
      loading.value = false
    }
  }

  function setFilters(newFilters: Partial<typeof filters.value>) {
    Object.assign(filters.value, newFilters)
    page.value = 1
  }

  function setPage(newPage: number) {
    page.value = newPage
  }

  return { devices, total, page, size, pages, loading, filters, fetchDevices, setFilters, setPage }
})
