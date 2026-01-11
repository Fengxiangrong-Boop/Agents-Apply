export interface LoginParams {
    username: string
    password: string
}

export interface RegisterParams {
    username: string
    email: string
    password: string
}

export interface LoginResponse {
    access_token: string
    token_type: string
}

export interface UserResponse {
    id: number
    username: string
    email: string
    is_active: boolean
    created_at: string
}
