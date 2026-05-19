<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="会员">
          <el-select v-model="searchForm.member_id" clearable filterable style="width: 180px" placeholder="可搜索">
            <el-option v-for="m in members" :key="m.id" :label="m.member_name + ' - ' + m.phone" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width: 240px" />
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
          <h3>销售记录</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
          <el-button type="primary" class="btn-large" @click="handleAdd"><Plus /> 开单销售</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="order_no" label="单号" width="180" />
        <el-table-column prop="member_name" label="会员" width="100">
          <template #default="{ row }">{{ row.member_name || '散客' }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="商品金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠" width="80">
          <template #default="{ row }">-¥{{ row.discount_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual_amount" label="实收" width="100">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">¥{{ row.actual_amount?.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="90">
          <template #default="{ row }">{{ payMethod[row.payment_method] }}</template>
        </el-table-column>
        <el-table-column prop="create_time" label="时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
            <el-button type="success" link @click="handlePrint(row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 开单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="950px" class="form-dialog">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="会员">
              <el-select v-model="form.member_id" clearable filterable style="width: 100%" placeholder="搜索会员" @change="onMemberChange">
                <el-option v-for="m in members" :key="m.id" :label="m.member_name + ' (' + m.phone + ')'" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="支付方式">
              <el-select v-model="form.payment_method" style="width: 100%">
                <el-option label="现金" value="cash" />
                <el-option label="微信支付" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="银行卡" value="card" />
                <el-option label="会员卡" value="member" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注">
              <el-input v-model="form.remark" placeholder="备注" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="商品">
          <div class="items-toolbar">
            <el-button type="primary" plain size="small" @click="showDrugDialog = true"><Plus /> 添加商品</el-button>
            <span style="margin-left: 20px; color: #909399;">会员积分: {{ currentMember?.points || 0 }}</span>
          </div>
          <el-table :data="form.items" border size="small" style="margin-top: 10px">
            <el-table-column label="药品" min-width="160">
              <template #default="{ row }">
                <span>{{ row.drug_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="spec" label="规格" width="100" />
            <el-table-column label="数量" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" :max="row.stock" size="small" style="width: 80px" @change="calcAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="100">
              <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="小计" width="100">
              <template #default="{ row }">¥{{ (row.quantity * row.price || 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button type="danger" link size="small" @click="form.items.splice($index, 1); calcTotal()">删</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="整单优惠">
              <el-input-number v-model="form.discount_amount" :min="0" :precision="2" size="large" style="width: 200px" @change="calcTotal" />
            </el-form-item>
          </el-col>
          <el-col :span="12" style="text-align: right;">
            <div class="total-info">
              <p>商品金额: <span>¥{{ form.total_amount?.toFixed(2) || '0.00' }}</span></p>
              <p>优惠金额: <span>-¥{{ form.discount_amount?.toFixed(2) || '0.00' }}</span></p>
              <p class="actual">实收金额: <span>¥{{ form.actual_amount?.toFixed(2) || '0.00' }}</span></p>
            </div>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="form-footer">
          <el-button size="large" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" size="large" class="btn-large" @click="handleSubmit">确认收款</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择药品弹窗 -->
    <el-dialog v-model="showDrugDialog" title="选择药品" width="700px">
      <div class="search-form" style="margin-bottom: 16px;">
        <el-input v-model="drugKeyword" placeholder="搜索药品名称/编码" clearable style="width: 300px" @input="loadDrugs">
          <template #prefix><Search /></template>
        </el-input>
      </div>
      <el-table :data="drugs" border size="small" max-height="400" @row-click="selectDrug">
        <el-table-column prop="drug_name" label="药品名称" />
        <el-table-column prop="spec" label="规格" width="100" />
        <el-table-column prop="price" label="零售价" width="80">
          <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="可用库存" width="100">
          <template #default="{ row }">{{ getStock(row.id) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="销售详情" width="650px" class="detail-dialog">
      <div v-if="currentOrder">
        <div class="detail-row"><span class="detail-label">单号</span><span class="detail-value">{{ currentOrder.order_no }}</span></div>
        <div class="detail-row"><span class="detail-label">会员</span><span class="detail-value">{{ currentOrder.member_name || '散客' }}</span></div>
        <div class="detail-row"><span class="detail-label">商品金额</span><span class="detail-value">¥{{ currentOrder.total_amount?.toFixed(2) }}</span></div>
        <div class="detail-row"><span class="detail-label">优惠金额</span><span class="detail-value">-¥{{ currentOrder.discount_amount?.toFixed(2) }}</span></div>
        <div class="detail-row"><span class="detail-label">实收金额</span><span class="detail-value" style="color: #f56c6c; font-weight: bold;">¥{{ currentOrder.actual_amount?.toFixed(2) }}</span></div>
        <div class="detail-row"><span class="detail-label">支付方式</span><span class="detail-value">{{ payMethod[currentOrder.payment_method] }}</span></div>
        <div class="detail-row"><span class="detail-label">时间</span><span class="detail-value">{{ currentOrder.create_time }}</span></div>
        <el-divider>商品明细</el-divider>
        <el-table :data="currentOrder.items" border size="small">
          <el-table-column prop="drug_name" label="药品" />
          <el-table-column prop="spec" label="规格" width="100" />
          <el-table-column prop="quantity" label="数量" width="60" />
          <el-table-column prop="price" label="单价" width="80"><template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template></el-table-column>
          <el-table-column prop="amount" label="小计" width="80"><template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template></el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'
import excel from '@/utils/excel'
import printer from '@/utils/printer'

const appStore = useAppStore()
const dateRange = ref([])
const drugKeyword = ref('')
const searchForm = reactive({ member_id: '', startDate: '', endDate: '' })
const tableData = ref([])
const total = ref(0)
const members = ref([])
const drugs = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const showDrugDialog = ref(false)
const dialogTitle = ref('开单销售')
const currentOrder = ref(null)
const currentMember = ref(null)

const form = reactive({
  member_id: '', payment_method: 'cash', remark: '', total_amount: 0, discount_amount: 0, actual_amount: 0, items: []
})

const payMethod = { cash: '现金', wechat: '微信', alipay: '支付宝', card: '银行卡', member: '会员卡' }
const drugStocks = ref({})

onMounted(() => { loadData(); loadMembers(); loadDrugs() })

const loadData = async () => {
  if (dateRange.value) {
    searchForm.startDate = dateRange.value[0]
    searchForm.endDate = dateRange.value[1] + ' 23:59:59'
  }
  const result = await api.sales.list(searchForm)
  if (result.success) { tableData.value = result.data || []; total.value = tableData.value.length }
}

const loadMembers = async () => {
  const result = await api.members.list({ status: '1' })
  if (result.success) members.value = result.data || []
}

const loadDrugs = async () => {
  const result = await api.drugs.list({ keyword: drugKeyword.value, status: '1' })
  if (result.success) {
    drugs.value = result.data || []
    // 加载库存
    for (const drug of drugs.value) {
      const batch = await api.inventory.getByDrugId(drug.id)
      drugStocks.value[drug.id] = batch.data?.reduce((sum, b) => sum + b.quantity, 0) || 0
    }
  }
}

const getStock = (drugId) => drugStocks.value[drugId] || 0

const handleReset = () => {
  Object.assign(searchForm, { member_id: '', startDate: '', endDate: '' })
  dateRange.value = []
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '开单销售'
  Object.assign(form, { member_id: '', payment_method: 'cash', remark: '', total_amount: 0, discount_amount: 0, actual_amount: 0, items: [] })
  currentMember.value = null
  dialogVisible.value = true
}

const onMemberChange = (memberId) => {
  currentMember.value = members.value.find(m => m.id === memberId)
}

const selectDrug = (row) => {
  if (row.stock <= 0) return ElMessage.warning('该药品库存不足')
  const exist = form.items.find(i => i.drug_id === row.id)
  if (exist) { exist.quantity++; calcAmount(exist) }
  else form.items.push({ drug_id: row.id, drug_name: row.drug_name, spec: row.spec, price: row.price, quantity: 1, amount: row.price })
  calcTotal()
  showDrugDialog.value = false
}

const calcAmount = (row) => { row.amount = row.quantity * row.price; calcTotal() }
const calcTotal = () => {
  form.total_amount = form.items.reduce((sum, item) => sum + (item.quantity * item.price || 0), 0)
  form.actual_amount = Math.max(0, form.total_amount - (form.discount_amount || 0))
}

const handleSubmit = async () => {
  if (!form.items.length) return ElMessage.warning('请添加商品')
  const result = await api.sales.create({ ...form, operator_id: appStore.userInfo?.id })
  if (result.success) {
    ElMessage.success('销售成功')
    // 打印小票
    const orderWithItems = { ...result.data, ...form, create_time: new Date().toLocaleString() }
    printer.printSalesTicket(orderWithItems, form.items, currentMember.value)
    dialogVisible.value = false
    loadData()
    loadDrugs()
  }
}

const handleDetail = async (row) => {
  const result = await api.sales.getById(row.id)
  if (result.success) currentOrder.value = result.data
  detailVisible.value = true
}

const handlePrint = async (row) => {
  const result = await api.sales.getById(row.id)
  if (result.success) {
    const member = row.member_id ? members.value.find(m => m.id === row.member_id) : null
    await printer.printSalesTicket(result.data, result.data.items, member)
    ElMessage.success('已发送打印')
  }
}

const handleExport = async () => {
  const result = await api.sales.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportSalesOrders(result.data)
  ElMessage.success('导出成功')
}
</script>

<style scoped lang="scss">
.total-info {
  p { margin: 8px 0; font-size: 15px; color: #606266; span { margin-left: 10px; } }
  .actual { font-size: 18px; color: #f56c6c; font-weight: bold; }
}
</style>
