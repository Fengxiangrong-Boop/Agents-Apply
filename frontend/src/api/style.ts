import http from '@/utils/http'

export interface Style {
    id: number
    name: string
    description: string
    prompt_instruction: string
    css_content: string
    preview_image?: string
    is_system: boolean
    created_at?: string
    updated_at?: string
}

export interface StyleCreate {
    name: string
    description: string
    prompt_instruction: string
    css_content: string
    preview_image?: string
}

export interface StyleUpdate {
    name?: string
    description?: string
    prompt_instruction?: string
    css_content?: string
    preview_image?: string
}

export const styleApi = {
    getStyles() {
        return http.get<any, Style[]>('/styles')
    },

    getStyle(id: number) {
        return http.get<any, Style>(`/styles/${id}`)
    },

    createStyle(data: StyleCreate) {
        return http.post<any, Style>('/styles', data)
    },

    updateStyle(id: number, data: StyleUpdate) {
        return http.put<any, Style>(`/styles/${id}`, data)
    },

    deleteStyle(id: number) {
        return http.delete(`/styles/${id}`)
    }
}
