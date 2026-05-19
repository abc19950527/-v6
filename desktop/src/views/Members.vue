<template>
  <div class="page-container">
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="姓名/手机/卡号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="searchForm.grade" clearable style="width: 120px">
            <el-option label="普通会员" value="普通会员" />
            <el-option label="银卡会员" value="银卡会员" />
            <el-option label="金卡会员" value="金卡会员" />
            <el-option label="VIP会员" value="VIP会员" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData"><Search /> 搜索</el-button>
          <el-button @click="Object.assign(searchForm, {keyword:'',grade:''}); loadData()"><Refresh /> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="data-table">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3>会员列表</h3>
          <span>共 {{ total }} 条</span>
        </div>
        <div class="toolbar-right">
          <el-button type="success" @click="handleExport"><Download /> 导出</el-button>
          <el-button type="primary" @click="handleAdd"><Plus /> 新增会员</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe size="large">
        <el-table-column prop="member_code" label="卡号" width="140" />
        <el-table-column prop="member_name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="grade" label="等级" width="90">
          <template #default="{ row }">
            <el-tag :type="gradeType[row.grade]" size="small">{{ row.grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="80" />
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="{ row }">¥{{ row.balance?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="birthday" label="生日" width="110" />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleRecharge(row)">充值</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="会员卡号" prop="member_code">
          <el-input v-model="form.member_code" placeholder="请输入卡号" />
        </el-form-item>
        <el-form-item label="姓名" prop="member_name">
          <el-input v-model="form.member_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="form.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="生日">
          <el-date-picker v-model="form.birthday" type="date" placeholder="选择生日" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="会员等级" prop="grade">
          <el-select v-model="form.grade" style="width: 100%">
            <el-option label="普通会员" value="普通会员" />
            <el-option label="银卡会员" value="银卡会员" />
            <el-option label="金卡会员" value="金卡会员" />
            <el-option label="VIP会员" value="VIP会员" />
          </el-select>
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

    <!-- 充值弹窗 -->
    <el-dialog v-model="rechargeVisible" title="会员充值" width="400px">
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="会员">{{ rechargeForm.member_name }}</el-form-item>
        <el-form-item label="当前余额">¥{{ rechargeForm.balance?.toFixed(2) || '0.00' }}</el-form-item>
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit">确定充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/database'
import excel from '@/utils/excel'

const searchForm = reactive({ keyword: '', grade: '' })
const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const rechargeVisible = ref(false)
const dialogTitle = ref('新增会员')
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null, member_code: '', member_name: '', phone: '', id_card: '', birthday: '', grade: '普通会员', status: '1'
})

const rechargeForm = reactive({ id: null, member_name: '', balance: 0, amount: 0 })

const gradeType = { '普通会员': 'info', '银卡会员': 'success', '金卡会员': 'warning', 'VIP会员': 'danger' }

const rules = {
  member_code: [{ required: true, message: '请输入卡号', trigger: 'blur' }],
  member_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }]
}

onMounted(() => loadData())

const loadData = async () => {
  const result = await api.members.list(searchForm)
  if (result.success) { tableData.value = result.data || []; total.value = tableData.value.length }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增会员'
  Object.assign(form, { id: null, member_code: 'HY' + Date.now(), member_name: '', phone: '', id_card: '', birthday: '', grade: '普通会员', status: '1' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑会员'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该会员?', '提示', { type: 'warning' })
  const result = await api.members.delete(row.id)
  if (result.success) { ElMessage.success('删除成功'); loadData() }
}

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    const result = isEdit.value ? await api.members.update(form.id, form) : await api.members.create(form)
    if (result.success) { ElMessage.success(isEdit.value ? '修改成功' : '新增成功'); dialogVisible.value = false; loadData() }
  })
}

const handleRecharge = (row) => {
  Object.assign(rechargeForm, { id: row.id, member_name: row.member_name, balance: row.balance, amount: 0 })
  rechargeVisible.value = true
}

const handleRechargeSubmit = async () => {
  if (!rechargeForm.amount) return ElMessage.warning('请输入充值金额')
  const result = await api.query('UPDATE members SET balance = balance + ? WHERE id = ?', [rechargeForm.amount, rechargeForm.id])
  if (result.success) {
    ElMessage.success('充值成功')
    rechargeVisible.value = false
    loadData()
  }
}

const handleExport = async () => {
  const result = await api.members.list({ ...searchForm, size: 10000 })
  if (result.success) await excel.exportMembers(result.data)
  ElMessage.success('导出成功')
}
</script>
