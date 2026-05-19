<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="姓名/账号/编码" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" clearable style="width: 120px">
            <el-option label="管理员" value="admin" />
            <el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData"><Search /> 搜索</el-button>
          <el-button @click="Object.assign(searchForm, {keyword:'',role:''}); loadData()"><Refresh /> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>员工列表</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
          <el-button type="primary" @click="handleAdd"><Plus /> 新增员工</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="staff_code" label="工号" width="100" />
        <el-table-column prop="staff_name" label="姓名" width="100" />
        <el-table-column prop="username" label="登录账号" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleChangePwd(row)">改密</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="工号" prop="staff_code">
          <el-input v-model="form.staff_code" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="姓名" prop="staff_name">
          <el-input v-model="form.staff_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入账号" :disabled="isEdit" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="登录密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio label="admin">管理员</el-radio>
            <el-radio label="staff">员工</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="1">启用</el-radio>
            <el-radio label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="form-footer">
          <el-button size="large" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="400px">
      <el-form :model="pwdForm" label-width="80px">
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="pwdForm.confirmPwd" type="password" show-password placeholder="请确认密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePwdSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import api from '@/api/database'
import excel from '@/utils/excel'

const searchForm = reactive({ keyword: '', role: '' })
const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const pwdDialogVisible = ref(false)
const dialogTitle = ref('新增员工')
const isEdit = ref(false)
const formRef = ref()
const currentUserId = ref(null)

const form = reactive({
  id: null, staff_code: '', staff_name: '', username: '', password: '', phone: '', id_card: '', role: 'staff', status: '1'
})

const pwdForm = reactive({ password: '', confirmPwd: '' })

const rules = {
  staff_code: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  staff_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

onMounted(() => loadData())

const loadData = async () => {
  const result = await api.staff.list(searchForm)
  if (result.success) {
    tableData.value = result.data || []
    total.value = tableData.value.length
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增员工'
  Object.assign(form, { id: null, staff_code: '', staff_name: '', username: '', password: '', phone: '', id_card: '', role: 'staff', status: '1' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑员工'
  Object.assign(form, row)
  form.password = ''
  dialogVisible.value = true
}

const handleChangePwd = (row) => {
  currentUserId.value = row.id
  pwdForm.password = ''
  pwdForm.confirmPwd = ''
  pwdDialogVisible.value = true
}

const handlePwdSubmit = async () => {
  if (!pwdForm.password) return ElMessage.warning('请输入新密码')
  if (pwdForm.password !== pwdForm.confirmPwd) return ElMessage.warning('两次密码不一致')
  const result = await api.staff.updatePassword(currentUserId.value, pwdForm.password)
  if (result.success) { ElMessage.success('修改成功'); pwdDialogVisible.value = false }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该员工?', '提示', { type: 'warning' })
  const result = await api.staff.delete(row.id)
  if (result.success) { ElMessage.success('删除成功'); loadData() }
}

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    const data = { ...form }
    if (!data.password) delete data.password
    const result = isEdit.value ? await api.staff.update(form.id, data) : await api.staff.create(data)
    if (result.success) { ElMessage.success(isEdit.value ? '修改成功' : '新增成功'); dialogVisible.value = false; loadData() }
  })
}

const handleExport = async () => {
  const result = await api.staff.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportStaff(result.data)
  ElMessage.success('导出成功')
}
</script>
