<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="info-card">
          <h3><el-icon><FolderOpened /></el-icon> 数据备份</h3>
          <p class="card-desc">将当前数据库完整备份到指定位置，建议定期进行数据备份以防止数据丢失。</p>
          
          <div class="backup-info">
            <p><span>当前数据库:</span> pharmacy.db</p>
            <p><span>备份位置:</span> 用户自定义</p>
          </div>
          
          <el-button type="primary" size="large" class="btn-large" @click="handleBackup">
            <el-icon><Download /></el-icon> 开始备份
          </el-button>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="info-card">
          <h3><el-icon><Upload /></el-icon> 数据恢复</h3>
          <p class="card-desc">从备份文件恢复数据库数据，恢复操作将覆盖当前数据，请谨慎操作！</p>
          
          <div class="warning-tip">
            <el-icon><Warning /></el-icon>
            <span>警告: 恢复操作会覆盖当前数据，建议恢复前先进行备份</span>
          </div>
          
          <el-button type="warning" size="large" class="btn-large" @click="handleRestore">
            <el-icon><Upload /></el-icon> 选择备份文件恢复
          </el-button>
        </div>
      </el-col>
    </el-row>

    <!-- 备份历史 -->
    <div class="info-card" style="margin-top: 20px;">
      <h3>备份记录</h3>
      <el-table :data="backupHistory" border size="small">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="create_time" label="备份时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleRestore">恢复</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 统计信息 -->
    <div class="info-card" style="margin-top: 20px;">
      <h3>数据统计</h3>
      <el-row :gutter="20">
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.drugs || 0 }}</p>
            <p class="stat-label">药品档案</p>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.suppliers || 0 }}</p>
            <p class="stat-label">供应商</p>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.staff || 0 }}</p>
            <p class="stat-label">员工</p>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.members || 0 }}</p>
            <p class="stat-label">会员</p>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.sales || 0 }}</p>
            <p class="stat-label">销售单</p>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <p class="stat-num">{{ dataStats.purchase || 0 }}</p>
            <p class="stat-label">采购单</p>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/database'

const backupHistory = ref([])
const dataStats = reactive({})

onMounted(() => {
  loadStats()
})

const loadStats = async () => {
  const tables = ['drugs', 'suppliers', 'staff', 'members', 'sales_orders', 'purchase_orders']
  for (const table of tables) {
    const result = await api.query(`SELECT COUNT(*) as count FROM ${table}`)
    if (result.success) {
      const key = table === 'sales_orders' ? 'sales' : table === 'purchase_orders' ? 'purchase' : table
      dataStats[key] = result.data[0]?.count || 0
    }
  }
}

const handleBackup = async () => {
  await ElMessageBox.confirm('确定要备份当前数据吗？', '数据备份', { type: 'info' })
  try {
    const result = await api.backup.backup()
    if (result.success) {
      ElMessage.success('备份成功！文件已保存到: ' + result.path)
    } else {
      ElMessage.error('备份失败: ' + result.error)
    }
  } catch (error) {
    ElMessage.error('备份失败: ' + error.message)
  }
}

const handleRestore = async () => {
  await ElMessageBox.confirm('恢复操作将覆盖当前所有数据！确定要继续吗？', '数据恢复', { type: 'warning' })
  try {
    const result = await api.backup.restore()
    if (result.success) {
      ElMessage.success('恢复成功！请重启应用使数据生效。')
    } else {
      if (result.error !== '取消恢复') {
        ElMessage.error('恢复失败: ' + result.error)
      }
    }
  } catch (error) {
    ElMessage.error('恢复失败: ' + error.message)
  }
}
</script>

<style scoped lang="scss">
.info-card {
  h3 {
    font-size: 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .card-desc {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 20px;
  }
  
  .backup-info {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    
    p {
      margin: 8px 0;
      color: #606266;
      
      span {
        color: #303133;
        font-weight: 500;
      }
    }
  }
  
  .warning-tip {
    background: #fff7e6;
    border: 1px solid #ffe7ba;
    padding: 12px 16px;
    border-radius: 8px;
    color: #fa8c16;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  
  .stat-num {
    font-size: 28px;
    font-weight: 600;
    color: #1890ff;
    margin-bottom: 8px;
  }
  
  .stat-label {
    font-size: 14px;
    color: #909399;
  }
}
</style>
