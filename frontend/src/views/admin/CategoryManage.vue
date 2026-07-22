<template>
  <div class="category-manage">
    <div class="page-header">
      <div>
        <h2>分类管理</h2>
        <p class="page-subtitle">管理平台设备分类</p>
      </div>
      <el-button type="primary" size="large" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增分类
      </el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="categories" v-loading="loading" stripe class="category-table">
        <el-table-column prop="name" label="分类名称" min-width="120">
          <template #default="{ row }">
            <span class="cat-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="80">
          <template #default="{ row }">
            <el-image v-if="row.icon" :src="row.icon" fit="contain" style="width: 32px; height: 32px" />
            <span v-else class="no-icon">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="device_count" label="设备数量" width="100">
          <template #default="{ row }">
            <span class="device-count-badge">{{ row.device_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small" effect="dark" round>
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新增分类'" width="440px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="50" size="large" />
        </el-form-item>
        <el-form-item label="图标URL" prop="icon">
          <el-input v-model="form.icon" placeholder="图标URL（选填）" size="large" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../../api/category'
import type { CategoryItem, CategoryCreate } from '../../api/category'

const loading = ref(false)
const categories = ref<CategoryItem[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<CategoryCreate & { sort_order: number }>({
  name: '',
  icon: '',
  sort_order: 0,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

onMounted(() => fetchCategories())

async function fetchCategories() {
  loading.value = true
  try {
    const resp = await getCategories()
    categories.value = resp.data.data
  } catch (e: any) {
    ElMessage.error(e.message || '获取分类失败')
  } finally {
    loading.value = false
  }
}

function openDialog(row?: CategoryItem) {
  editingId.value = row?.id || null
  form.name = row?.name || ''
  form.icon = row?.icon || ''
  form.sort_order = row?.sort_order ?? 0
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { name: form.name, icon: form.icon || undefined, sort_order: form.sort_order }
    if (editingId.value) {
      await updateCategory(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createCategory(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchCategories()
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: CategoryItem) {
  if (row.device_count > 0) {
    ElMessage.warning('该分类下存在设备，无法删除')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, '提示', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    await fetchCategories()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}
</script>

<style scoped>
.category-manage {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
  animation: fadeInUp 0.5s ease-out;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 26px;
  color: var(--color-foreground);
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-muted-foreground);
  margin: 4px 0 0;
}

.table-wrapper {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.category-table {
  --el-table-border-color: var(--color-border);
  --el-table-header-bg-color: var(--color-muted);
}

.cat-name {
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-foreground);
}

.no-icon {
  color: var(--color-muted-foreground);
}

.device-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 24px;
  padding: 0 8px;
  border-radius: 12px;
  background: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-foreground);
}
</style>
