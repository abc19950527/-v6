<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="药品名称" clearable style="width: 200px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData"><Search /> 搜索</el-button>
          <el-button @click="Object.assign(searchForm, {keyword:''}); loadData()"><Refresh /> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>库存列表</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="drug_name" label="药品名称" min-width="150" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="batch_number" label="批次号" width="120" />
        <el-table-column prop="production_date" label="生产日期" width="110" />
        <el-table-column prop="expiry_date" label="有效期" width="110" />
        <el-table-column prop="quantity" label="库存数量" width="90">
          <template #default="{ row }">
            <span :style="{ color: row.quantity <= row.min_stock ? '#f56c6c' : '' }">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价" width="80">
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="price" label="零售价" width="80">
          <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="供应商" min-width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleAdjust(row)">调整</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 调整库存弹窗 -->
    <el-dialog v-model="adjustVisible" title="调整库存" width="400px">
      <el-form :model="adjustForm" label-width="80px">
        <el-form-item label="药品">{{ adjustForm.drug_name }}</el-form-item>
        <el-form-item label="批次号">{{ adjustForm.batch_number }}</el-form-item>
        <el-form-item label="当前库存">{{ adjustForm.quantity }}</el-form-item>
        <el-form-item label="新库存">
          <el-input-number v-model="adjustForm.new_quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="adjustForm.reason" type="textarea" placeholder="请输入调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdjustSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'
import excel from '@/utils/excel'

const appStore = useAppStore()
const searchForm = reactive({ keyword: '' })
const tableData = ref([])
const total = ref(0)
const adjustVisible = ref(false)
const adjustForm = reactive({ id: null, drug_name: '', batch_number: '', quantity: 0, new_quantity: 0, reason: '' })

onMounted(() => loadData())

const loadData = async () => {
  const result = await api.inventory.list(searchForm)
  if (result.success) { tableData.value = result.data || []; total.value = tableData.value.length }
}

const handleAdjust = (row) => {
  Object.assign(adjustForm, { id: row.id, drug_name: row.drug_name, batch_number: row.batch_number, quantity: row.quantity, new_quantity: row.quantity, reason: '' })
  adjustVisible.value = true
}

const handleAdjustSubmit = async () => {
  const result = await api.inventory.updateQuantity(adjustForm.id, adjustForm.new_quantity)
  if (result.success) {
    await api.logs.add(appStore.userInfo?.id, '库存调整', `调整${adjustForm.drug_name}库存: ${adjustForm.quantity} -> ${adjustForm.new_quantity}, 原因: ${adjustForm.reason}`)
    ElMessage.success('调整成功')
    adjustVisible.value = false
    loadData()
  }
}

const handleExport = async () => {
  const result = await api.inventory.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportInventory(result.data)
  ElMessage.success('导出成功')
}
</script>
