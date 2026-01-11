
import http from '@/utils/http'

export interface ApiKeyConfig {
    id?: number
    provider: string
    api_key: string
    is_valid?: boolean
}

export const apiKeyApi = {
    getApiKey(provider: string = 'siliconflow') {
        return http.get<any, ApiKeyConfig | null>('/api-keys', { params: { provider } })
    },
    createApiKey(data: ApiKeyConfig) {
        return http.post<any, ApiKeyConfig>('/api-keys', data)
    },
    updateApiKey(data: ApiKeyConfig) {
        return http.put<any, ApiKeyConfig>('/api-keys', data)
    },
    deleteApiKey(provider: string = 'siliconflow') {
        return http.delete('/api-keys', { params: { provider } })
    }
}
