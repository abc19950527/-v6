// 数据库操作 API 模块
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 药品管理
export const drugsAPI = {
  list: (params) => api.get('/drugs', { params }),
  getById: (id) => api.get(`/drugs/${id}`),
  create: (data) => api.post('/drugs', data),
  update: (id, data) => api.put(`/drugs/${id}`, data),
  delete: (id) => api.delete(`/drugs/${id}`)
}

// 供应商管理
export const suppliersAPI = {
  list: (params) => api.get('/suppliers', { params }),
  getById: (id) => api.get(`/suppliers/${id}`),
  create: (data) => api.post('/suppliers', data),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  delete: (id) => api.delete(`/suppliers/${id}`)
}

// 员工管理
export const staffAPI = {
  list: (params) => api.get('/staff', { params }),
  getById: (id) => api.get(`/staff/${id}`),
  create: (data) => api.post('/staff', data),
  update: (id, data) => api.put(`/staff/${id}`, data),
  delete: (id) => api.delete(`/staff/${id}`),
  login: (data) => api.post('/staff/login', data),
  changePwd: (data) => api.post('/staff/changePwd', data)
}

// 会员管理
export const membersAPI = {
  list: (params) => api.get('/members', { params }),
  getById: (id) => api.get(`/members/${id}`),
  create: (data) => api.post('/members', data),
  update: (id, data) => api.put(`/members/${id}`, data),
  delete: (id) => api.delete(`/members/${id}`),
  charge: (id, data) => api.post(`/members/${id}/charge`, data)
}

// 入库管理
export const purchaseAPI = {
  list: (params) => api.get('/purchases', { params }),
  getById: (id) => api.get(`/purchases/${id}`),
  create: (data) => api.post('/purchases', data),
  update: (id, data) => api.put(`/purchases/${id}`, data),
  delete: (id) => api.delete(`/purchases/${id}`)
}

// 销售管理
export const salesAPI = {
  list: (params) => api.get('/sales', { params }),
  getById: (id) => api.get(`/sales/${id}`),
  create: (data) => api.post('/sales', data),
  delete: (id) => api.delete(`/sales/${id}`),
  todaySummary: () => api.get('/sales/todaySummary')
}

// 库存管理
export const inventoryAPI = {
  list: (params) => api.get('/inventory', { params }),
  getByDrugId: (drugId) => api.get(`/inventory/drug/${drugId}`),
  adjust: (data) => api.post('/inventory/adjust', data),
  check: () => api.post('/inventory/check', data),
  expiryWarning: () => api.get('/inventory/expiryWarning'),
  lowStock: () => api.get('/inventory/lowStock')
}

// 报表统计
export const reportsAPI = {
  getSalesSummary: (params) => api.get('/reports/salesSummary', { params }),
  getTopDrugs: (params) => api.get('/reports/topDrugs', { params }),
  getLowStockDrugs: () => api.get('/reports/lowStockDrugs'),
  getInventoryValue: () => api.get('/reports/inventoryValue'),
  getDailySales: (params) => api.get('/reports/dailySales', { params }),
  getMonthlySales: (params) => api.get('/reports/monthlySales', { params })
}

// 操作日志
export const logsAPI = {
  list: (params) => api.get('/logs', { params }),
  create: (data) => api.post('/logs', data)
}

// 数据备份
export const backupAPI = {
  create: () => api.post('/backup/create'),
  restore: (filePath) => api.post('/backup/restore', { filePath }),
  list: () => api.get('/backup/list'),
  download: (id) => api.get(`/backup/download/${id}`, { responseType: 'blob' })
}

// 系统设置
export const settingsAPI = {
  get: () => api.get('/settings'),
  update: (data) => api.put('/settings', data)
}

export default {
  drugs: drugsAPI,
  suppliers: suppliersAPI,
  staff: staffAPI,
  members: membersAPI,
  purchases: purchaseAPI,
  sales: salesAPI,
  inventory: inventoryAPI,
  reports: reportsAPI,
  logs: logsAPI,
  backup: backupAPI,
  settings: settingsAPI
}
