<template>
  <el-container class="layout-container">
    <!-- 左侧导航 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>药品管理系统</h2>
        <p>v6.0</p>
      </div>
      
      <el-menu 
        :default-active="activeMenu" 
        class="sidebar-menu"
        :router="true"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-menu-item index="/drugs">
          <el-icon><MedicinesBox /></el-icon>
          <span>药品档案</span>
        </el-menu-item>
        
        <el-menu-item index="/suppliers">
          <el-icon><OfficeBuilding /></el-icon>
          <span>供应商管理</span>
        </el-menu-item>
        
        <el-menu-item index="/staff">
          <el-icon><User /></el-icon>
          <span>员工管理</span>
        </el-menu-item>
        
        <el-menu-item index="/purchase">
          <el-icon><ShoppingCartFull /></el-icon>
          <span>采购入库</span>
        </el-menu-item>
        
        <el-menu-item index="/sales">
          <el-icon><Sell /></el-icon>
          <span>销售出库</span>
        </el-menu-item>
        
        <el-menu-item index="/inventory">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
        </el-menu-item>
        
        <el-menu-item index="/members">
          <el-icon><UserFilled /></el-icon>
          <span>会员管理</span>
        </el-menu-item>
        
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计报表</span>
        </el-menu-item>
        
        <el-menu-item index="/backup">
          <el-icon><FolderOpened /></el-icon>
          <span>数据备份</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <h3>{{ currentTitle }}</h3>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ userInfo?.staff_name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="changePwd">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const userInfo = computed(() => appStore.userInfo)

const activeMenu = computed(() => route.path)

const menuTitles = {
  '/dashboard': '首页',
  '/drugs': '药品档案管理',
  '/suppliers': '供应商管理',
  '/staff': '员工管理',
  '/purchase': '采购入库管理',
  '/sales': '销售出库管理',
  '/inventory': '库存管理',
  '/members': '会员管理',
  '/reports': '统计报表',
  '/backup': '数据备份恢复'
}

const currentTitle = computed(() => menuTitles[activeMenu.value] || '')

const handleCommand = async (command) => {
  switch (command) {
    case 'logout':
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      appStore.clearUserInfo()
      router.push('/login')
      break
    case 'changePwd':
      router.push('/staff?action=changePwd')
      break
    case 'profile':
      ElMessageBox.alert(`姓名: ${userInfo.value?.staff_name}<br>角色: ${userInfo.value?.role === 'admin' ? '管理员' : '员工'}`, '个人信息')
      break
  }
}

onMounted(() => {
  // 监听菜单备份恢复事件
  if (window.electronAPI) {
    window.electronAPI.onMenuBackup(() => {
      router.push('/backup?action=backup')
    })
    window.electronAPI.onMenuRestore(() => {
      router.push('/backup?action=restore')
    })
  }
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  
  .logo {
    height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    color: #fff;
    
    h2 {
      font-size: 18px;
      margin-bottom: 4px;
    }
    
    p {
      font-size: 12px;
      opacity: 0.8;
    }
  }
}

.header {
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .header-left h3 {
    font-size: 18px;
    color: #303133;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background 0.3s;
    
    &:hover {
      background: #f5f7fa;
    }
  }
}

.main {
  padding: 20px;
  background: #f0f2f5;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
