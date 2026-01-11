import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// 创建 axios 实例
const http: AxiosInstance = axios.create({
    baseURL: '/api/v1', // 配合 vite proxy
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
http.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 从 localStorage 获取 token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error: AxiosError) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
http.interceptors.response.use(
    (response: AxiosResponse) => {
        // 直接返回数据部分
        return response.data
    },
    (error: AxiosError) => {
        // 处理 401 未授权
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            // 可以跳转到登录页，或者通过 global event bus 通知
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default http
