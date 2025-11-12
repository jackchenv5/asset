import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/Login.vue'
import Layout from '@/layouts/Layout.vue'
import Dashboard from '@/views/Dashboard.vue'
import BarcodeSummary from '@/views/BarcodeSummary.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/',
      component: Layout,
      redirect: '/barcode-summary',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'barcode-summary',
          name: 'BarcodeSummary',
          component: BarcodeSummary,
          meta: { title: '条码汇总' }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 尝试获取用户信息来检查是否已登录
  if (!authStore.isAuthenticated && to.path !== '/login') {
    try {
      await authStore.getUserInfoAction()
      next()
    } catch (error) {
      next('/login')
    }
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router