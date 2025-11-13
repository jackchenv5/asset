<template>
  <div class="layout-container">
    <!-- 整合的顶部导航栏 -->
    <el-header class="layout-header">
      <div class="header-content">
        <div class="header-left">
          <h2>资产管理系统</h2>
          <el-menu
            :default-active="$route.path"
            class="header-menu"
            background-color="transparent"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/barcode-summary">
              <el-icon><Document /></el-icon>
              <span>条码汇总</span>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-icon><User /></el-icon>
              {{ userInfo?.username || '用户' }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">账户设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <!-- 主内容区域 -->
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import { House, Box, TrendCharts, Setting, User, Document } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const userInfo = computed(() => authStore.user)

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
      await authStore.logoutAction()
      router.push('/login')
    } catch (error) {
      // 用户点击取消或发生错误，不执行任何操作
      console.log('退出登录取消或失败:', error)
    }
  } else if (command === 'profile') {
    // TODO: 跳转到个人信息页面
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  background-color: #2c3e50;
  color: white;
  padding: 0;
  height: 6vh;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  white-space: nowrap;
}

.header-menu {
  border-bottom: none;
  height: 6vh;
}

.header-menu .el-menu-item {
  height: 6vh;
  line-height: 60px;
  border-bottom: none;
}

.header-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.header-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2);
  border-bottom: none;
}

.user-dropdown {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.layout-main {
  flex: 1;
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}
</style>