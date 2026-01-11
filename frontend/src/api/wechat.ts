import http from '@/utils/http'

export interface WechatConfig {
    id?: number
    app_id: string
    app_secret: string
    access_token?: string
    token_expires_at?: string
}

export const wechatApi = {
    getConfig() {
        return http.get<any, WechatConfig | null>('/wechat/config')
    },
    createConfig(data: WechatConfig) {
        return http.post<any, WechatConfig>('/wechat/config', data)
    },
    updateConfig(data: WechatConfig) {
        return http.put<any, WechatConfig>('/wechat/config', data)
    },
    deleteConfig() {
        return http.delete('/wechat/config')
    }
}
