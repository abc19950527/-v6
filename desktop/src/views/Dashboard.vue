<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card info-card">
          <div class="stat-icon blue">
            <MedicinesBox />
          </div>
          <div class="stat-content">
            <p class="stat-title">药品数量</p>
            <p class="stat-value">{{ stats.drugCount }}</p>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card info-card">
          <div class="stat-icon green">
            <ShoppingCartFull />
          </div>
          <div class="stat-content">
            <p class="stat-title">今日采购</p>
            <p class="stat-value">¥{{ stats.todayPurchase }}</p>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card info-card">
          <div class="stat-icon orange">
            <Sell />
          </div>
          <div class="stat-content">
            <p class="stat-title">今日销售</p>
            <p class="stat-value">¥{{ stats.todaySales }}</p>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card info-card">
          <div class="stat-icon red">
            <WarningFilled />
          </div>
          <div class="stat-content">
            <p class="stat-title">库存预警</p>
            <p class="stat-value">{{ stats.lowStockCount }}</p>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="chart-card info-card">
          <h3>近7天销售趋势</h3>
          <div ref="salesChartRef" class="chart-container"></div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="chart-card info-card">
          <h3>快捷操作</h3>
          <div class="quick-actions">
            <el-button type="primary" size="large" class="action-btn" @click="$router.push('/sales')">
              <Sell /> 销售开单
            </el-button>
            <el-button type="success" size="large" class="action-btn" @click="$router.push('/purchase')">
              <ShoppingCartFull /> 采购入库
            </el-button>
            <el-button type="warning" size="large" class="action-btn" @click="$router.push('/drugs')">
              <MedicinesBox /> 药品查询
            </el-button>
            <el-button type="info" size="large" class="action-btn" @click="$router.push('/inventory')">
              <Box /> 库存盘点
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 列表区域 -->
    <el-row :gutter="20" class="list-row">
      <el-col :span="12">
        <div class="info-card">
          <h3>库存预警</h3>
          <el-table :data="lowStockList" size="small" max-height="250">
            <el-table-column prop="drug_name" label="药品名称" />
            <el-table-column prop="spec" label="规格" width="100" />
            <el-table-column prop="total_stock" label="当前库存" width="80" />
            <el-table-column prop="min_stock" label="最低库存" width="80" />
          </el-table>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="info-card">
          <h3>近期销售</h3>
          <el-table :data="recentSales" size="small" max-height="250">
            <el-table-column prop="order_no" label="单号" width="140" />
            <el-table-column prop="member_name" label="会员" width="80">
              <template #default="{ row }">
                {{ row.member_name || '散客' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_amount" label="金额" width="80">
              <template #default="{ row }">
                ¥{{ row.actual_amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="时间" width="140" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import api from '@/api/database'
import * as echarts from 'echarts'

const stats = reactive({
  drugCount: 0,
  todayPurchase: 0,
  todaySales: 0,
  lowStockCount: 0
})

const lowStockList = ref([])
const recentSales = ref([])
const salesChartRef = ref(null)

onMounted(async () => {
  await loadStats()
  await loadLowStock()
  await loadRecentSales()
  initChart()
})

const loadStats = async () => {
  // 药品数量
  const drugs = await api.drugs.list()
  stats.drugCount = drugs.data?.length || 0
  
  // 今日采购
  const today = new Date().toISOString().slice(0, 10)
  const purchaseSummary = await api.reports.getPurchaseSummary({ startDate: today, endDate: today + ' 23:59:59' })
  stats.todayPurchase = purchaseSummary.data?.total_amount || 0
  
  // 今日销售
  const salesSummary = await api.reports.getSalesSummary({ startDate: today, endDate: today + ' 23:59:59' })
  stats.todaySales = salesSummary.data?.total_actual || 0
  
  // 库存预警
  const lowStock = await api.reports.getLowStockDrugs()
  stats.lowStockCount = lowStock.data?.length || 0
}

const loadLowStock = async () => {
  const result = await api.reports.getLowStockDrugs()
  lowStockList.value = result.data?.slice(0, 10) || []
}

const loadRecentSales = async () => {
  const result = await api.sales.list()
  recentSales.value = result.data?.slice(0, 10) || []
}

const initChart = async () => {
  if (!salesChartRef.value) return
  
  const chart = echarts.init(salesChartRef.value)
  const dates = []
  const salesData = []
  
  // 获取近7天数据
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().slice(0, 10)
    dates.push(dateStr.slice(5))
    
    const result = await api.reports.getSalesSummary({ 
      startDate: dateStr, 
      endDate: dateStr + ' 23:59:59' 
    })
    salesData.push(result.data?.total_actual || 0)
  }
  
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value' },
    series: [{
      name: '销售额',
      type: 'line',
      smooth: true,
      data: salesData,
      areaStyle: { color: 'rgba(24, 144, 255, 0.2)' },
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    }]
  }
  
  chart.setOption(option)
}
</script>

<style scoped lang="scss">
.dashboard {
  .stat-row {
    margin-bottom: 20px;
  }
  
  .stat-card {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .stat-icon {
      width: 64px;
      height: 64px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      
      &.blue { background: rgba(24, 144, 255, 0.1); color: #1890ff; }
      &.green { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
      &.orange { background: rgba(250, 173, 20, 0.1); color: #faad14; }
      &.red { background: rgba(255, 77, 79, 0.1); color: #ff4d4f; }
    }
    
    .stat-content {
      .stat-title {
        color: #909399;
        font-size: 14px;
        margin-bottom: 8px;
      }
      
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
    
    .chart-card {
      h3 {
        font-size: 16px;
        margin-bottom: 16px;
        color: #303133;
      }
      
      .chart-container {
        height: 280px;
      }
    }
  }
  
  .list-row {
    .info-card {
      h3 {
        font-size: 16px;
        margin-bottom: 16px;
        color: #303133;
      }
    }
  }
  
  .quick-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    
    .action-btn {
      height: 60px;
      font-size: 15px;
      
      :deep(.el-icon) {
        margin-right: 8px;
      }
    }
  }
}
</style>
