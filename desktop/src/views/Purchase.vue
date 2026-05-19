<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="供应商">
          <el-select v-model="searchForm.supplier_id" clearable style="width: 180px" placeholder="请选择">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.supplier_name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable style="width: 120px">
            <el-option label="待入库" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData"><Search /> 搜索</el-button>
          <el-button @click="handleReset"><Refresh /> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>采购入库单</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
          <el-button type="primary" @click="handleAdd"><Plus /> 新增进货单</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="order_no" label="单号" width="180" />
        <el-table-column prop="supplier_name" label="供应商" width="150" />
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_status" label="付款状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 'paid' ? 'success' : 'warning'" size="small">
              {{ row.payment_status === 'paid' ? '已付款' : '未付款' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]" size="small">{{ statusText[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handleComplete(row)">入库</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="900px" class="form-dialog">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="form.supplier_id" placeholder="请选择供应商" style="width: 100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.supplier_name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input v-model="form.remark" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="商品明细">
          <div class="items-toolbar">
            <el-button type="primary" plain size="small" @click="handleAddItem"><Plus /> 添加商品</el-button>
          </div>
          <el-table :data="form.items" border size="small" style="margin-top: 10px">
            <el-table-column label="药品" min-width="150">
              <template #default="{ row, $index }">
                <el-select v-model="row.drug_id" placeholder="选择药品" style="width: 100%" @change="onDrugChange(row)">
                  <el-option v-for="d in drugs" :key="d.id" :label="d.drug_name" :value="d.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="批次号" width="120">
              <template #default="{ row }">
                <el-input v-model="row.batch_number" placeholder="批次号" />
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 80px" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width: 100px" @change="calcAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="金额" width="100">
              <template #default="{ row }">{{ (row.quantity * row.price || 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button type="danger" link size="small" @click="form.items.splice($index, 1); calcTotal()">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <el-form-item label="总金额">
          <span style="font-size: 20px; color: #f56c6c; font-weight: bold;">¥{{ form.total_amount?.toFixed(2) || '0.00' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="form-footer">
          <el-button size="large" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit">确定入库</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="入库单详情" width="700px" class="detail-dialog">
      <div v-if="currentOrder">
        <div class="detail-row"><span class="detail-label">单号</span><span class="detail-value">{{ currentOrder.order_no }}</span></div>
        <div class="detail-row"><span class="detail-label">供应商</span><span class="detail-value">{{ currentOrder.supplier_name }}</span></div>
        <div class="detail-row"><span class="detail-label">总金额</span><span class="detail-value">¥{{ currentOrder.total_amount?.toFixed(2) }}</span></div>
        <div class="detail-row"><span class="detail-label">状态</span><span class="detail-value">{{ statusText[currentOrder.status] }}</span></div>
        <div class="detail-row"><span class="detail-label">创建时间</span><span class="detail-value">{{ currentOrder.create_time }}</span></div>
        <div class="detail-row"><span class="detail-label">备注</span><span class="detail-value">{{ currentOrder.remark || '-' }}</span></div>
        <el-divider>商品明细</el-divider>
        <el-table :data="currentOrder.items" border size="small">
          <el-table-column prop="drug_name" label="药品" />
          <el-table-column prop="spec" label="规格" width="100" />
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column prop="price" label="单价" width="80">
            <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="80">
            <template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'
import excel from '@/utils/excel'
import printer from '@/utils/printer'

const appStore = useAppStore()
const dateRange = ref([])
const searchForm = reactive({ supplier_id: '', status: '', startDate: '', endDate: '' })
const tableData = ref([])
const total = ref(0)
const suppliers = ref([])
const drugs = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const dialogTitle = ref('新增采购单')
const currentOrder = ref(null)

const form = reactive({
  supplier_id: '', remark: '', total_amount: 0, items: []
})

const statusType = { pending: 'warning', completed: 'success', cancelled: 'info' }
const statusText = { pending: '待入库', completed: '已完成', cancelled: '已取消' }

onMounted(() => {
  loadData()
  loadSuppliers()
  loadDrugs()
})

const loadData = async () => {
  if (dateRange.value) {
    searchForm.startDate = dateRange.value[0]
    searchForm.endDate = dateRange.value[1] + ' 23:59:59'
  }
  const result = await api.purchase.list(searchForm)
  if (result.success) {
    tableData.value = result.data || []
    total.value = tableData.value.length
  }
}

const loadSuppliers = async () => {
  const result = await api.suppliers.list({ status: '1' })
  if (result.success) suppliers.value = result.data || []
}

const loadDrugs = async () => {
  const result = await api.drugs.list({ status: '1' })
  if (result.success) drugs.value = result.data || []
}

const handleReset = () => {
  Object.assign(searchForm, { supplier_id: '', status: '', startDate: '', endDate: '' })
  dateRange.value = []
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '新增采购单'
  Object.assign(form, { supplier_id: '', remark: '', total_amount: 0, items: [] })
  dialogVisible.value = true
}

const handleAddItem = () => {
  form.items.push({ drug_id: '', batch_number: '', quantity: 1, price: 0, amount: 0 })
}

const onDrugChange = (row) => {
  const drug = drugs.value.find(d => d.id === row.drug_id)
  if (drug) row.price = drug.cost_price || 0
  calcAmount(row)
}

const calcAmount = (row) => {
  row.amount = row.quantity * row.price
  calcTotal()
}

const calcTotal = () => {
  form.total_amount = form.items.reduce((sum, item) => sum + (item.quantity * item.price || 0), 0)
}

const handleSubmit = async () => {
  if (!form.supplier_id) return ElMessage.warning('请选择供应商')
  if (!form.items.length) return ElMessage.warning('请添加商品')
  calcTotal()
  const result = await api.purchase.create({
    ...form,
    operator_id: appStore.userInfo?.id,
    status: 'completed'
  })
  if (result.success) {
    ElMessage.success('入库成功')
    dialogVisible.value = false
    loadData()
  }
}

const handleDetail = async (row) => {
  const result = await api.purchase.getById(row.id)
  if (result.success) currentOrder.value = result.data
  detailVisible.value = true
}

const handleComplete = async (row) => {
  await ElMessageBox.confirm('确认该单已入库?', '提示', { type: 'warning' })
  const result = await api.purchase.updateStatus(row.id, 'completed')
  if (result.success) { ElMessage.success('入库成功'); loadData() }
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm('确定取消该单?', '提示', { type: 'warning' })
  const result = await api.purchase.updateStatus(row.id, 'cancelled')
  if (result.success) { ElMessage.success('已取消'); loadData() }
}

const handleExport = async () => {
  const result = await api.purchase.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportPurchaseOrders(result.data)
  ElMessage.success('导出成功')
}
</script>
