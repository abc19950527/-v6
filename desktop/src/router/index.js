import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'Odometer' }
      },
      {
        path: 'drugs',
        name: 'Drugs',
        component: () => import('@/views/Drugs.vue'),
        meta: { title: '药品档案', icon: 'MedicinesBox' }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/Suppliers.vue'),
        meta: { title: '供应商管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'staff',
        name: 'Staff',
        component: () => import('@/views/Staff.vue'),
        meta: { title: '员工管理', icon: 'User' }
      },
      {
        path: 'purchase',
        name: 'Purchase',
        component: () => import('@/views/Purchase.vue'),
        meta: { title: '采购入库', icon: 'ShoppingCartFull' }
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/Sales.vue'),
        meta: { title: '销售出库', icon: 'Sell' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/Inventory.vue'),
        meta: { title: '库存管理', icon: 'Box' }
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/Members.vue'),
        meta: { title: '会员管理', icon: 'UserFilled' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { title: '统计报表', icon: 'DataAnalysis' }
      },
      {
        path: 'backup',
        name: 'Backup',
        component: () => import('@/views/Backup.vue'),
        meta: { title: '数据备份', icon: 'FolderOpened' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 药品进销存管理系统v6`
  }
  
  const userInfo = localStorage.getItem('userInfo')
  if (!userInfo && to.path !== '/login') {
    next('/login')
  } else {
    next()
  }
})

export default router
