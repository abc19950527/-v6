<template>
  <div class="page-container">
    <!-- 日期选择 -->
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 280px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData"><Search /> 查询</el-button>
          <el-button @click="setThisMonth">本月</el-button>
          <el-button @click="setThisYear">本年</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="info-card stat-card">
          <p class="card-title">销售订单数</p>
          <p class="card-value">{{ stats.total_orders || 0 }}</p>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-card stat-card">
          <p class="card-title">总销售额</p>
          <p class="card-value" style="color: #f56c6c;">¥{{ stats.total_sales?.toFixed(2) || '0.00' }}</p>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-card stat-card">
          <p class="card-title">实收金额</p>
          <p class="card-value" style="color: #67c23a;">¥{{ stats.total_actual?.toFixed(2) || '0.00' }}</p>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-card stat-card">
          <p class="card-title">平均客单价</p>
          <p class="card-value">¥{{ stats.avg_order?.toFixed(2) || '0.00' }}</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="info-card">
          <h3>销售排行榜TOP10</h3>
          <el-table :data="topDrugs" border size="small" max-height="350">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="drug_name" label="药品名称" />
            <el-table-column prop="spec" label="规格" width="100" />
            <el-table-column prop="total_qty" label="销售数量" width="90" />
            <el-table-column prop="total_amount" label="销售金额" width="100">
              <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="info-card">
          <h3>库存预警</h3>
          <el-table :data="lowStockList" border size="small" max-height="350">
            <el-table-column prop="drug_name" label="药品名称" />
            <el-table-column prop="spec" label="规格" width="100" />
            <el-table-column prop="total_stock" label="当前库存" width="90">
              <template #default="{ row }"><span style="color: #f56c6c;">{{ row.total_stock }}</span></template>
            </el-table-column>
            <el-table-column prop="min_stock" label="最低库存" width="90" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 操作日志 -->
    <div class="info-card" style="margin-top: 20px;">
      <h3>操作日志</h3>
      <el-table :data="logs" border size="small" max-height="300">
        <el-table-column prop="staff_name" label="操作人" width="100" />
        <el-table-column prop="operation" label="操作类型" width="100" />
        <el-table-column prop="detail" label="操作详情" />
        <el-table-column prop="create_time" label="时间" width="160" />
      </el-table>
    </div>

    <div style="text-align: center; margin-top: 20px;">
      <el-button type="success" size="large" @click="handleExport"><Download /> 导出统计报表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/database'
import excel from '@/utils/excel'

const dateRange = ref([])
const searchForm = reactive({ startDate: '', endDate: '' })
const stats = ref({})
const topDrugs = ref([])
const lowStockList = ref([])
const logs = ref([])

onMounted(() => {
  const now = new Date()
  dateRange.value = [now.toISOString().slice(0, 7) + '-01', now.toISOString().slice(0, 10)]
  loadData()
})

const loadData = async () => {
  if (dateRange.value) {
    searchForm.startDate = dateRange.value[0]
    searchForm.endDate = dateRange.value[1] + ' 23:59:59'
  }
  
  // 加载统计数据
  const salesResult = await api.reports.getSalesSummary(searchForm)
  if (salesResult.success) stats.value = salesResult.data || {}
  
  // 销售排行
  const topResult = await api.reports.getTopDrugs(searchForm)
  if (topResult.success) topDrugs.value = topResult.data || []
  
  // 库存预警
  const lowStockResult = await api.reports.getLowStockDrugs()
  if (lowStockResult.success) lowStockList.value = lowStockResult.data || []
  
  // 操作日志
  const logsResult = await api.logs.list({})
  if (logsResult.success) logs.value = logsResult.data?.slice(0, 20) || []
}

const setThisMonth = () => {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), 1)
  dateRange.value = [start.toISOString().slice(0, 10), now.toISOString().slice(0, 10)]
  loadData()
}

const setThisYear = () => {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 1)
  dateRange.value = [start.toISOString().slice(0, 10), now.toISOString().slice(0, 10)]
  loadData()
}

const handleExport = async () => {
  await excel.exportSalesReport(stats.value)
  ElMessage.success('导出成功')
}
</script>

<style scoped lang="scss">
.info-card {
  h3 {
    font-size: 16px;
    margin-bottom: 16px;
    color: #303133;
  }
}
</style>
