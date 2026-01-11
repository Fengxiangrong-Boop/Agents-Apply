
import http from '@/utils/http'
import type { LoginParams, RegisterParams, LoginResponse, UserResponse } from '@/types/auth'

export const authApi = {
    login(data: LoginParams) {
        return http.post<any, LoginResponse>('/auth/login', data)
    },
    register(data: RegisterParams) {
        return http.post<any, UserResponse>('/auth/register', data) // 后端返回 UserResponse
    },
    getCurrentUser() {
        return http.get<any, UserResponse>('/users/me')
    }
}
