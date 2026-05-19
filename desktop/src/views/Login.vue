<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-logo">
        <h1>药品进销存管理系统</h1>
        <p>Pharmacy Management System v6.0</p>
      </div>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            class="btn-large login-btn"
            style="width: 100%"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tip">
        <p>默认账号: admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'

const router = useRouter()
const appStore = useAppStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const result = await api.staff.login(loginForm.username, loginForm.password)
      
      if (result.success && result.data) {
        const userInfo = {
          id: result.data.id,
          staff_code: result.data.staff_code,
          staff_name: result.data.staff_name,
          role: result.data.role,
          username: result.data.username
        }
        appStore.setUserInfo(userInfo)
        
        // 记录登录日志
        await api.logs.add(userInfo.id, '登录', `用户${userInfo.staff_name}登录系统`)
        
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } else {
        ElMessage.error('用户名或密码错误')
      }
    } catch (error) {
      ElMessage.error('登录失败: ' + error.message)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .login-box {
    width: 420px;
    padding: 40px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    
    .login-logo {
      text-align: center;
      margin-bottom: 30px;
      
      h1 {
        font-size: 24px;
        color: #1890ff;
        margin-bottom: 8px;
      }
      
      p {
        color: #909399;
        font-size: 14px;
      }
    }
    
    .login-btn {
      font-size: 16px;
    }
    
    .login-tip {
      margin-top: 20px;
      text-align: center;
      color: #909399;
      font-size: 12px;
    }
  }
}
</style>
