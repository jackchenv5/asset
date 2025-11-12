<template>
  <div class="barcode-summary-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form" label-width="70px">
        <div class="form-row">
          <el-form-item label="条码" class="compact-item">
            <el-input v-model="filterForm.barcode" placeholder="条码" clearable size="small" />
          </el-form-item>
          <el-form-item label="型号" class="compact-item">
            <el-input v-model="filterForm.model" placeholder="型号" clearable size="small" />
          </el-form-item>
          <el-form-item label="位置" class="compact-item">
            <el-input v-model="filterForm.location" placeholder="位置" clearable size="small" />
          </el-form-item>
          <el-form-item label="扫描人员" class="compact-item">
            <el-input v-model="filterForm.scanner" placeholder="扫描人" clearable size="small" />
          </el-form-item>
          <el-form-item label="备注" class="compact-item">
            <el-input v-model="filterForm.remarks" placeholder="备注" clearable size="small" />
          </el-form-item>
  
          <el-form-item label="使用人" class="compact-item">
            <el-input v-model="filterForm.user" placeholder="使用人" clearable size="small" />
          </el-form-item>
          <el-form-item label="资产类型" class="compact-item">
            <el-select v-model="filterForm.asset_type" placeholder="资产类型" clearable size="small" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="工厂借用" value="工厂借用" />
              <el-option label="研发样机" value="研发样机" />
            </el-select>
          </el-form-item>
          <el-form-item label="处理状态" class="compact-item">
            <el-select v-model="filterForm.result" placeholder="处理状态" clearable size="small" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="已完成" value="true" />
              <el-option label="处理中" value="false" />
            </el-select>
          </el-form-item>
          <el-form-item class="button-group">
            <el-button type="primary" @click="handleSearch" size="small">搜索</el-button>
            <el-button @click="handleReset" size="small">重置</el-button>
            <el-button @click="handleExport" size="small">导出</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-card>

    <el-card class="table-card">
        <vxe-grid
          ref="xGrid"
          v-bind="gridOptions"
          :data="tableData"
        />
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
          style="display: flex; justify-content: flex-end;"
        />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      title="编辑对话框"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="条码">
          <el-input v-model="formData.barcode" disabled />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="formData.model" disabled />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="formData.location" disabled />
        </el-form-item>
        <el-form-item label="扫描人员">
          <el-input v-model="formData.scanner" disabled />
        </el-form-item>
        <el-form-item label="时间">
          <el-input v-model="formData.scan_time" disabled />
        </el-form-item>
        <el-form-item label="使用人">
          <el-input v-model="formData.user" disabled />
        </el-form-item>
        <el-form-item label="资产类型">
          <el-input v-model="formData.asset_type" disabled />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-switch v-model="formData.result" active-text="已完成" inactive-text="处理中" />
        </el-form-item>
        <el-form-item label="预计处理时间">
          <el-date-picker v-model="formData.expected_time" type="datetime" placeholder="选择时间" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="3" disabled />
        </el-form-item>
        <el-form-item label="处理结果备注">
          <el-input v-model="formData.result_remarks" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      title="导入条码汇总"
      v-model="importDialogVisible"
      width="600px"
    >
      <el-upload
        drag
        :action="uploadAction"
        :headers="uploadHeaders"
        accept=".xlsx,.xls"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
      >
        <el-icon><Upload /></el-icon>
        <div>将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div>只能上传xlsx/xls文件</div>
        </template>
      </el-upload>
      
      <div v-if="importResult" style="margin-top: 20px;">
        <el-alert
          :title="`导入完成：成功 ${importResult.success_count} 条，失败 ${importResult.error_count} 条`"
          :type="importResult.error_count > 0 ? 'warning' : 'success'"
          show-icon
        >
          <div v-if="importResult.errors && importResult.errors.length > 0">
            <div v-for="(error, index) in importResult.errors.slice(0, 5)" :key="index">
              {{ error }}
            </div>
            <div v-if="importResult.errors.length > 5">... 还有 {{ importResult.errors.length - 5 }} 条错误</div>
          </div>
        </el-alert>
      </div>
      
      <div style="margin-top: 20px; text-align: center;">
        <el-button @click="handleExportTemplate">下载导入模板</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import request from '@/utils/request'
import { ref, reactive, onMounted, onUnmounted, h } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 工具函数定义
const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

// 获取当前用户信息
const authStore = useAuthStore()
const currentUser = ref(null)

// 获取用户显示名称
const getUserDisplayName = (user) => {
  if (!user) return ''
  const lastName = user.last_name || ''
  const firstName = user.first_name || ''
  const fullName = `${lastName}${firstName}`.trim()
  return fullName || user.username || ''
}

// 分页处理
const handlePageChange = () => {
  fetchData()
}

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const xGrid = ref(null)
const formRef = ref(null)
const tableHeight = ref(400) // 默认表格高度
const totalCount = ref(0) // 总记录数
const currentPage = ref(1) // 当前页码
const pageSize = ref(20) // 每页条数

// 筛选表单
const filterForm = reactive({
  barcode: '',
  model: '',
  location: '',
  scanner: '',
  scan_time: '',
  remarks: '',
  user: '', // 将在获取用户信息后设置默认值
  asset_type: '',
  result: '',
  start_time: '',
  end_time: '',
  code_type: ''
})

// 对话框数据
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const dialogTitle = ref('编辑')
const importResult = ref(null)

const formData = reactive({
  id: '',
  barcode: '',
  model: '',
  location: '',
  scanner: '',
  scan_time: '',
  remarks: '',
  user: '',
  asset_type: '',
  result: '',
  expected_time: '',
  result_remarks: ''
})

const formRules = {
  barcode: [{ required: true, message: '请输入条码', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }]
}

// 导入对话框配置
const uploadAction = '/api/asset-code/import-barcode-summary/'
const uploadHeaders = {
  'X-CSRFToken': getCookie('csrftoken')
}

// 表格配置
const gridOptions = reactive({
  loading: false,
  height: tableHeight, // 动态高度
  border: true,
  showOverflow: true,
  showHeaderOverflow: true,
  columns: [
    { type: 'seq', width: 50, title: '序号', align: 'center' },
    { field: 'barcode', title: '条码', width: 160, showOverflow: true },
    { field: 'model', title: '型号', width: 180, showOverflow: true },
    { field: 'location', title: '位置', width: 180, showOverflow: true },
    { field: 'scanner', title: '扫描人员', width: 120, align: 'center' },
    { field: 'scan_time', title: '扫描时间', width: 150, align: 'center' },
    { field: 'user', title: '使用人', width: 120, align: 'center', showOverflow: true },
    { field: 'asset_type', title: '资产类型', width: 120, align: 'center' },
    { 
      field: 'result', 
      title: '处理状态', 
      width: 120, 
      align: 'center',
      slots: {
        default: ({ row }) => [
          h('div', {
            style: {
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px'
            }
          }, [
            h('i', {
              class: row.result ? 'el-icon-check' : 'el-icon-time',
              style: {
                color: row.result ? '#67c23a' : '#e6a23c',
                fontSize: '14px'
              }
            }),
            h('span', {
              style: {
                fontSize: '12px',
                color: row.result ? '#67c23a' : '#e6a23c',
                fontWeight: '500'
              }
            }, row.result ? '已完成' : '处理中')
          ])
        ]
      }
    },
    { 
      field: 'expected_time', 
      title: '预计处理时间', 
      width: 150, 
      align: 'center',
      formatter: ({ cellValue }) => {
        if (!cellValue) return '-'
        try {
          const date = new Date(cellValue)
          const year = date.getFullYear()
          const month = String(date.getMonth() + 1).padStart(2, '0')
          const day = String(date.getDate()).padStart(2, '0')
          const hours = String(date.getHours()).padStart(2, '0')
          const minutes = String(date.getMinutes()).padStart(2, '0')
          return `${year}-${month}-${day} ${hours}:${minutes}`
        } catch (error) {
          return cellValue
        }
      }
    },
    { 
      field: 'result_remarks', 
      title: '处理结果备注', 
      minWidth: 200, 
      showOverflow: true 
    },
    { 
      field: 'action', 
      title: '操作', 
      width: 80, 
      align: 'center',
      slots: {
        default: ({ row }) => [
          h('button', {
            style: {
              padding: '6px 10px',
              backgroundColor: '#409eff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: '32px',
              height: '28px',
              fontSize: '12px'
            },
            title: '编辑',
            onClick: () => handleEdit(row)
          }, '编辑')
        ]
      }
    }
  ]
})

// 生命周期
onMounted(async () => {
  try {
    // 获取当前用户信息
    currentUser.value = authStore.user
    
    // 设置使用人默认值为当前登录用户（last_name + first_name）
    if (currentUser.value) {
      filterForm.user = getUserDisplayName(currentUser.value)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  
  fetchData()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})

// 方法定义
const fetchData = async () => {
  gridOptions.loading = true
  try {
    const params = {
      ...filterForm,
      page: currentPage.value,
      page_size: pageSize.value
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await request.get('/asset-code/barcode-summaries/', { params })
    tableData.value = response.data.results || response.data
    totalCount.value = response.data.count || response.data.length || 0
  } catch (error) {
    console.log(error)
    ElMessage.error('获取数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    gridOptions.loading = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  filterForm.user = ''
  filterForm.start_time = ''
  filterForm.end_time = ''
  filterForm.status = ''
  filterForm.code_type = ''
  fetchData()
}

const handleEdit = (row) => {
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessage.error('删除功能已禁用')
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    await request.put(`/asset-code/barcode-summaries/${formData.id}/`, formData)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleExport = async () => {
  try {
    const params = {
      ...filterForm,
      export: true
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await request.get('/asset-code/barcode-summaries/export/', { 
      params,
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '条码汇总.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleUploadSuccess = (response) => {
  importResult.value = response
  ElMessage.success('导入成功')
  fetchData()
}

const handleUploadError = (error) => {
  ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
}

const handleExportTemplate = async () => {
  try {
    const response = await request.get('/asset-code/export-barcode-summary-template/', { 
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '条码汇总导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 计算表格高度
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight
  console.log(windowHeight)
  if (windowHeight > 900) {
    tableHeight.value = 680
  }else{
    tableHeight.value = 480
  }
}

</script>

<style scoped>
.barcode-summary-container {
  margin: 0px;
  padding: 0px;
  height: 89vh;
  display: flex;
  flex-direction: column;
}

.filter-form {
  margin: 0px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.compact-item {
  margin-bottom: 0 !important;
  margin-right: 0 !important;
}

.compact-item .el-form-item__label {
  padding-right: 8px !important;
  font-size: 12px;
  line-height: 28px;
}

.compact-item .el-form-item__content {
  line-height: 28px;
}

.compact-item .el-input--small {
  width: 120px;
}

.compact-item .el-select--small {
  width: 120px;
}

.button-group {
  margin-bottom: 0 !important;
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.button-group .el-button--small {
  padding: 7px 15px;
}

.edit-btn {
  padding: 6px 10px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 28px;
}

.edit-btn:hover {
  background-color: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.edit-btn:active {
  background-color: #3a8ee6;
  transform: translateY(0);
}

.edit-btn .el-icon-edit {
  color: white;
  font-weight: 500;
}

.filter-card{
}

.table-card {
  margin-top: 0px;
  min-height: 0px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

</style>