import axios from 'axios'

// 获取 CSRF token 的函数
const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
}

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true  // 启用cookie
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 获取 CSRF token
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    // 如果是 POST, PUT, DELETE 等需要 CSRF 的请求，确保有 Content-Type
    if (['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
      if (!config.headers['Content-Type']) {
        config.headers['Content-Type'] = 'application/json'
      }
    }
    
    // 原有的 token 认证
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request