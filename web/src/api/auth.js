import request from '@/utils/request'

export const login = (data) => {
  return request({
    url: '/auth/login/',
    method: 'post',
    data,
    withCredentials: true  // 启用cookie
  })
}

export const logout = () => {
  return request({
    url: '/auth/logout/',
    method: 'post',
    withCredentials: true  // 启用cookie
  })
}

export const getUserInfo = () => {
  return request({
    url: '/auth/user/',
    method: 'get',
    withCredentials: true  // 启用cookie
  })
}