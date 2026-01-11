import http from '@/utils/http'

export interface Style {
    id: number
    name: string
    description: string
    prompt_instruction: string
    css_content: string
    preview_image?: string
    is_system: boolean
}

export interface Article {
    id: number
    title: string
    prompt_input: string
    content_html: string
    status: 'draft' | 'synced' | 'failed'
    synced_at?: string
    created_at: string
}

export interface ArticleCreate {
    style_id: number
    prompt_input: string
}

export const articleApi = {
    getStyles() {
        return http.get<any, Style[]>('/styles')
    },

    createArticle(data: ArticleCreate) {
        // LLM 生成可能比较慢，设置较长超时已在全局配置，这里也可单独配置
        return http.post<any, Article>('/articles', data, { timeout: 120000 })
    },

    getArticle(id: number) {
        return http.get<any, Article>(`/articles/${id}`)
    },

    syncArticle(id: number) {
        return http.post<any, any>(`/articles/${id}/sync`)
    },

    getArticles(params?: { skip?: number, limit?: number }) {
        return http.get<any, Article[]>('/articles', { params })
    }
}
