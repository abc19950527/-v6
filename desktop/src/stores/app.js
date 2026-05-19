import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 用户信息
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  
  // 系统配置
  const config = ref({
    shopName: '药品进销存管理系统',
    printerType: '58mm',
    autoBackup: true
  })

  // 是否登录
  const isLoggedIn = computed(() => !!userInfo.value)

  // 设置用户信息
  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  // 清除用户信息
  function clearUserInfo() {
    userInfo.value = null
    localStorage.removeItem('userInfo')
  }

  // 更新配置
  function updateConfig(newConfig) {
    config.value = { ...config.value, ...newConfig }
    localStorage.setItem('appConfig', JSON.stringify(config.value))
  }

  // 加载配置
  function loadConfig() {
    const savedConfig = localStorage.getItem('appConfig')
    if (savedConfig) {
      config.value = JSON.parse(savedConfig)
    }
  }

  return {
    userInfo,
    config,
    isLoggedIn,
    setUserInfo,
    clearUserInfo,
    updateConfig,
    loadConfig
  }
})
