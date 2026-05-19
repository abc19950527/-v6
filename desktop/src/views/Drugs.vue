<template>
  <div class="page-container">
    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="药品名称/编码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="请选择" clearable style="width: 150px">
            <el-option label="西药" value="西药" />
            <el-option label="中成药" value="中成药" />
            <el-option label="中药材" value="中药材" />
            <el-option label="保健品" value="保健品" />
            <el-option label="医疗器械" value="医疗器械" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px">
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 数据表格 -->
    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>药品列表</h3>
          <span class="total-count">共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon> 导出
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增药品
          </el-button>
        </div>
      </div>
      
      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="drug_code" label="药品编码" width="120" />
        <el-table-column prop="drug_name" label="药品名称" min-width="150" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="category" label="分类" width="80" />
        <el-table-column prop="manufacturer" label="生产厂家" min-width="150" show-overflow-tooltip />
        <el-table-column prop="price" label="零售价" width="90">
          <template #default="{ row }">
            ¥{{ row.price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价" width="90">
          <template #default="{ row }">
            ¥{{ row.cost_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="prescription_type" label="处方类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.prescription_type === 'OTC' ? 'success' : 'warning'" size="small">
              {{ row.prescription_type === 'OTC' ? '非处方药' : '处方药' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>
    
    <!-- 新增/编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="600px" 
      class="form-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="药品编码" prop="drug_code">
          <el-input v-model="form.drug_code" placeholder="请输入药品编码" />
        </el-form-item>
        <el-form-item label="药品名称" prop="drug_name">
          <el-input v-model="form.drug_name" placeholder="请输入药品名称" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="规格" prop="spec">
              <el-input v-model="form.spec" placeholder="如: 10mg*10片" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" placeholder="如: 盒/瓶" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="西药" value="西药" />
                <el-option label="中成药" value="中成药" />
                <el-option label="中药材" value="中药材" />
                <el-option label="保健品" value="保健品" />
                <el-option label="医疗器械" value="医疗器械" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="处方类型" prop="prescription_type">
              <el-radio-group v-model="form.prescription_type">
                <el-radio label="OTC">非处方药</el-radio>
                <el-radio label="RX">处方药</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="生产厂家" prop="manufacturer">
          <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
        </el-form-item>
        <el-form-item label="批准文号" prop="approval_number">
          <el-input v-model="form.approval_number" placeholder="请输入批准文号" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="零售价" prop="price">
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="成本价" prop="cost_price">
              <el-input-number v-model="form.cost_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最低库存" prop="min_stock">
              <el-input-number v-model="form.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="1">启用</el-radio>
            <el-radio label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="form-footer">
          <el-button size="large" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/database'
import excel from '@/utils/excel'

const searchForm = reactive({
  keyword: '',
  category: '',
  status: ''
})

const tableData = ref([])
const total = ref(0)
const pagination = reactive({
  page: 1,
  size: 10
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增药品')
const formRef = ref()
const isEdit = ref(false)

const form = reactive({
  id: null,
  drug_code: '',
  drug_name: '',
  spec: '',
  unit: '盒',
  category: '',
  manufacturer: '',
  approval_number: '',
  price: 0,
  cost_price: 0,
  min_stock: 0,
  prescription_type: 'OTC',
  status: '1'
})

const rules = {
  drug_code: [{ required: true, message: '请输入药品编码', trigger: 'blur' }],
  drug_name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }]
}

onMounted(() => {
  loadData()
})

const loadData = async () => {
  const result = await api.drugs.list({
    ...searchForm,
    page: pagination.page,
    size: pagination.size
  })
  if (result.success) {
    tableData.value = result.data || []
    total.value = tableData.value.length
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  Object.assign(searchForm, { keyword: '', category: '', status: '' })
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增药品'
  Object.assign(form, {
    id: null,
    drug_code: '',
    drug_name: '',
    spec: '',
    unit: '盒',
    category: '',
    manufacturer: '',
    approval_number: '',
    price: 0,
    cost_price: 0,
    min_stock: 0,
    prescription_type: 'OTC',
    status: '1'
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑药品'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该药品吗？', '提示', { type: 'warning' })
    const result = await api.drugs.delete(row.id)
    if (result.success) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (isEdit.value) {
        const result = await api.drugs.update(form.id, form)
        if (result.success) {
          ElMessage.success('修改成功')
        }
      } else {
        const result = await api.drugs.create(form)
        if (result.success) {
          ElMessage.success('新增成功')
        }
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      ElMessage.error('操作失败: ' + error.message)
    }
  })
}

const handleExport = async () => {
  const result = await api.drugs.list({ ...searchForm, size: 10000 })
  if (result.success && result.data) {
    await excel.exportDrugs(result.data)
    ElMessage.success('导出成功')
  }
}
</script>

<style scoped lang="scss">
.page-container {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      
      h3 {
        font-size: 16px;
        margin: 0;
      }
      
      .total-count {
        color: #909399;
        font-size: 14px;
      }
    }
  }
}
</style>
