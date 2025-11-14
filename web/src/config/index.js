// 环境变量配置
export const config = {
  // API配置
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002',
  API_PREFIX: import.meta.env.VITE_API_PREFIX || '/api',
  
  // 应用信息
  APP_NAME: import.meta.env.VITE_APP_NAME || '资产管理系统',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // 获取完整的API地址
  getFullApiUrl: (path) => {
    return `${config.API_BASE_URL}${config.API_PREFIX}${path}`
  }
}

// 调试输出当前配置（开发环境）
if (import.meta.env.DEV) {
  console.log('当前环境配置:', {
    API_BASE_URL: config.API_BASE_URL,
    API_PREFIX: config.API_PREFIX,
    APP_NAME: config.APP_NAME,
    APP_VERSION: config.APP_VERSION
  })
}