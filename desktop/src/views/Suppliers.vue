<template>
  <div class="page-container">
    <!-- 搜索 -->
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="供应商名称/编码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable style="width: 120px">
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><Search /> 搜索</el-button>
          <el-button @click="handleReset"><Refresh /> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>供应商列表</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
          <el-button type="primary" @click="handleAdd"><Plus /> 新增</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="supplier_code" label="编码" width="120" />
        <el-table-column prop="supplier_name" label="供应商名称" min-width="150" />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="供应商编码" prop="supplier_code">
          <el-input v-model="form.supplier_code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="供应商名称" prop="supplier_name">
          <el-input v-model="form.supplier_name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" placeholder="请输入地址" />
        </el-form-item>
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

const searchForm = reactive({ keyword: '', status: '' })
const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('新增供应商')
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null, supplier_code: '', supplier_name: '', contact: '', phone: '', address: '', status: '1'
})

const rules = {
  supplier_code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  supplier_name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

onMounted(() => loadData())

const loadData = async () => {
  const result = await api.suppliers.list(searchForm)
  if (result.success) {
    tableData.value = result.data || []
    total.value = tableData.value.length
  }
}

const handleSearch = () => loadData()
const handleReset = () => { Object.assign(searchForm, { keyword: '', status: '' }); loadData() }

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增供应商'
  Object.assign(form, { id: null, supplier_code: '', supplier_name: '', contact: '', phone: '', address: '', status: '1' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑供应商'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除?', '提示', { type: 'warning' })
  const result = await api.suppliers.delete(row.id)
  if (result.success) { ElMessage.success('删除成功'); loadData() }
}

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    const result = isEdit.value ? await api.suppliers.update(form.id, form) : await api.suppliers.create(form)
    if (result.success) {
      ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    }
  })
}

const handleExport = async () => {
  const result = await api.suppliers.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportSuppliers(result.data)
  ElMessage.success('导出成功')
}
</script>
