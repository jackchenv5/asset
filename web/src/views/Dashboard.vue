<template>
  <div class="dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>欢迎使用资产管理系统</span>
        </div>
      </template>
      <div class="dashboard-content">
        <h2>系统功能</h2>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="8">
            <el-card shadow="hover">
              <el-icon size="48" color="#409EFF">
                <Box />
              </el-icon>
              <h3>资产管理</h3>
              <p>管理企业各类资产信息</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <el-icon size="48" color="#67C23A">
                <TrendCharts />
              </el-icon>
              <h3>报表统计</h3>
              <p>资产统计与数据分析</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <el-icon size="48" color="#E6A23C">
                <Setting />
              </el-icon>
              <h3>系统设置</h3>
              <p>系统配置与权限管理</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 仪表板页面
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.dashboard-content h2 {
  color: #333;
  margin-bottom: 20px;
}

.el-card {
  text-align: center;
}

.el-icon {
  margin-bottom: 15px;
}

h3 {
  color: #606266;
  margin: 10px 0;
}

p {
  color: #909399;
  font-size: 14px;
}
</style>