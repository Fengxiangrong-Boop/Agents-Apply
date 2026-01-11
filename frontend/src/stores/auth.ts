import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import type { LoginParams } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<any>(null)

    function setToken(newToken: string) {
        token.value = newToken
        localStorage.setItem('token', newToken)
    }

    function clearToken() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    async function login(params: LoginParams) {
        try {
            const data = await authApi.login(params)
            setToken(data.access_token)
            await fetchUser()
            return true
        } catch (error) {
            console.error('Login failed', error)
            throw error // 让 UI 层处理错误提示
        }
    }

    async function fetchUser() {
        if (!token.value) return
        try {
            user.value = await authApi.getCurrentUser()
        } catch (error) {
            console.error('Fetch user failed', error)
            clearToken() // Token 可能过期或无效
        }
    }

    return { token, user, setToken, clearToken, login, fetchUser }
})

