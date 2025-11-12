<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="background-animation">
      <div class="bg-bubbles">
        <div v-for="n in 15" :key="n" :class="`bubble bubble-${n}`"></div>
      </div>
      <div class="floating-shapes">
        <div v-for="n in 6" :key="n" :class="`shape shape-${n}`"></div>
      </div>
    </div>
    
    <!-- 渐变遮罩 -->
    <div class="gradient-overlay"></div>
    
    <!-- 登录卡片 -->
    <div class="login-wrapper">
      <el-card class="login-card">
        <template #header>
          <div class="card-header">
            <div class="logo-container">
              <div class="logo-wrapper">
                <div class="logo-icon">
                  <i class="el-icon-s-management"></i>
                </div>
                <div class="logo-glow"></div>
              </div>
            </div>
            <h2 class="login-title">资产管理系统</h2>
            <p class="login-subtitle">Asset Management System</p>
          </div>
        </template>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              @keyup.enter="handleLogin"
              size="large"
            >
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
              size="large"
            >
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              @click="handleLogin"
              :loading="loading"
              class="login-button"
              size="large"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登 录 中...</span>
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.loginAction(loginForm)
        ElMessage.success('登录成功')
        // 登录成功后获取用户信息
        await authStore.getUserInfoAction()
        router.push('/')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 添加粒子效果
const createParticles = () => {
  const container = document.querySelector('.background-animation')
  if (!container) return
  
  for (let i = 0; i < 20; i++) {
    const particle = document.createElement('div')
    particle.className = 'particle'
    const opacity = (Math.random() * 0.3 + 0.1).toFixed(2)
    particle.style.cssText = `
      position: absolute;
      width: ${Math.random() * 4 + 1}px;
      height: ${Math.random() * 4 + 1}px;
      background: rgba(74, 144, 226, ${opacity});
      border-radius: 50%;
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 100}%;
      animation: particleFloat ${Math.random() * 10 + 10}s infinite linear;
      animation-delay: ${Math.random() * 5}s;
    `
    container.appendChild(particle)
  }
}

onMounted(() => {
  createParticles()
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(-45deg, #4a90e2, #357abd, #2c5aa0, #1e3a8a);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

/* 动态背景渐变 */
@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 背景动画容器 */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

/* 渐变遮罩 */
.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(74, 144, 226, 0.8) 0%,
    rgba(44, 90, 160, 0.8) 100%
  );
  z-index: 2;
}

/* 登录包装器 */
.login-wrapper {
  position: relative;
  z-index: 10;
}

/* 登录卡片 */
.login-card {
  width: 420px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  animation: cardFloat 6s ease-in-out infinite;
  margin: 20px;
}

@keyframes cardFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 卡片头部 */
.card-header {
  text-align: center;
  padding: 40px 0 30px;
  background: linear-gradient(135deg, #4a90e2 0%, #2c5aa0 100%);
  margin: -30px -30px 30px;
  color: white;
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: headerGlow 4s ease-in-out infinite;
}

@keyframes headerGlow {
  0%, 100% { opacity: 0.3; transform: rotate(0deg); }
  50% { opacity: 0.6; transform: rotate(180deg); }
}

.logo-container {
  margin-bottom: 20px;
  position: relative;
  z-index: 2;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: logoPulse 3s ease-in-out infinite;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 3;
}

.logo-icon i {
  font-size: 32px;
  color: white;
  animation: iconFloat 2s ease-in-out infinite;
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  animation: glowPulse 4s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
  }
  50% { 
    transform: scale(1.05);
    box-shadow: 0 0 40px rgba(255, 255, 255, 0.3);
  }
}

@keyframes iconFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.4; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

.login-title {
  margin: 0;
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-subtitle {
  margin: 0;
  font-size: 15px;
  opacity: 0.85;
  font-weight: 300;
  letter-spacing: 1px;
  position: relative;
  z-index: 2;
}

/* 登录表单 */
.login-form {
  padding: 0 30px 20px;
}

:deep(.el-form-item) {
  margin-bottom: 25px;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 20px rgba(74, 144, 226, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);
}

.login-button {
  width: 100%;
  border-radius: 10px;
  background: linear-gradient(135deg, #4a90e2 0%, #2c5aa0 100%);
  border: none;
  font-size: 16px;
  font-weight: 500;
  padding: 12px 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(74, 144, 226, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

/* 气泡动画 */
.bg-bubbles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.bubble {
  position: absolute;
  background: rgba(74, 144, 226, 0.15);
  border: 1px solid rgba(74, 144, 226, 0.3);
  border-radius: 50%;
  animation: float 20s infinite ease-in-out;
}

.bubble::before {
  content: '';
  position: absolute;
  top: 15%;
  left: 25%;
  width: 30%;
  height: 30%;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  filter: blur(1px);
}

.bubble::after {
  content: '';
  position: absolute;
  top: 60%;
  left: 70%;
  width: 15%;
  height: 15%;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  filter: blur(1px);
}

.bubble-1 { width: 80px; height: 80px; left: 10%; animation-delay: 0s; animation-duration: 25s; }
.bubble-2 { width: 60px; height: 60px; left: 20%; animation-delay: 2s; animation-duration: 20s; }
.bubble-3 { width: 100px; height: 100px; left: 35%; animation-delay: 4s; animation-duration: 30s; }
.bubble-4 { width: 40px; height: 40px; left: 50%; animation-delay: 6s; animation-duration: 18s; }
.bubble-5 { width: 70px; height: 70px; left: 65%; animation-delay: 8s; animation-duration: 22s; }
.bubble-6 { width: 90px; height: 90px; left: 80%; animation-delay: 10s; animation-duration: 28s; }
.bubble-7 { width: 50px; height: 50px; left: 90%; animation-delay: 12s; animation-duration: 24s; }
.bubble-8 { width: 65px; height: 65px; left: 15%; animation-delay: 14s; animation-duration: 26s; }
.bubble-9 { width: 85px; height: 85px; left: 70%; animation-delay: 16s; animation-duration: 32s; }
.bubble-10 { width: 55px; height: 55px; left: 85%; animation-delay: 18s; animation-duration: 20s; }

@keyframes float {
  0% {
    transform: translateY(100vh) translateX(0) scale(0.8);
    opacity: 0;
  }
  10% {
    opacity: 1;
    transform: translateY(90vh) translateX(-10px) scale(1);
  }
  50% {
    transform: translateY(50vh) translateX(20px) scale(1.1);
  }
  90% {
    opacity: 1;
    transform: translateY(10vh) translateX(-15px) scale(0.9);
  }
  100% {
    transform: translateY(-100px) translateX(0) scale(0.8);
    opacity: 0;
  }
}

/* 浮动形状 */
.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: rgba(74, 144, 226, 0.05);
  animation: shapeFloat 15s infinite ease-in-out;
}

.shape-1 {
  width: 120px;
  height: 120px;
  top: 20%;
  left: 5%;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  animation-delay: 0s;
  animation-duration: 18s;
}

.shape-2 {
  width: 80px;
  height: 80px;
  top: 60%;
  left: 85%;
  border-radius: 53% 47% 43% 57% / 51% 39% 61% 49%;
  animation-delay: 3s;
  animation-duration: 22s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  top: 80%;
  left: 25%;
  border-radius: 25% 75% 75% 25% / 25% 25% 75% 75%;
  animation-delay: 6s;
  animation-duration: 20s;
}

.shape-4 {
  width: 60px;
  height: 60px;
  top: 30%;
  left: 75%;
  border-radius: 67% 33% 19% 81% / 65% 77% 23% 35%;
  animation-delay: 9s;
  animation-duration: 16s;
}

.shape-5 {
  width: 90px;
  height: 90px;
  top: 70%;
  left: 10%;
  border-radius: 41% 59% 65% 35% / 43% 57% 43% 57%;
  animation-delay: 12s;
  animation-duration: 24s;
}

.shape-6 {
  width: 70px;
  height: 70px;
  top: 10%;
  left: 60%;
  border-radius: 50% 50% 33% 67% / 55% 45% 55% 45%;
  animation-delay: 15s;
  animation-duration: 19s;
}

@keyframes shapeFloat {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0.3;
  }
  25% {
    transform: translate(30px, -30px) rotate(90deg);
    opacity: 0.6;
  }
  50% {
    transform: translate(-20px, 20px) rotate(180deg);
    opacity: 0.4;
  }
  75% {
    transform: translate(40px, 10px) rotate(270deg);
    opacity: 0.7;
  }
}

/* 粒子动画 */
@keyframes particleFloat {
  0% {
    transform: translateY(0px) translateX(0px);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(-50px);
    opacity: 0;
  }
}

/* 粒子效果 */
.particle {
  pointer-events: none;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    margin: 0 20px;
  }
  
  .login-form {
    padding: 0 20px 20px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .login-subtitle {
    font-size: 12px;
  }
}
</style>