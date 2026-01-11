import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Register.vue')
    },
    {
        path: '/',
        component: () => import('@/layouts/MainLayout.vue'),
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue')
            },
            {
                path: 'articles',
                name: 'Articles',
                component: () => import('@/views/Articles.vue')
            },
            {
                path: 'styles',
                name: 'Styles',
                component: () => import('@/views/Styles.vue')
            },
            {
                path: 'settings',
                name: 'Settings',
                component: () => import('@/views/Settings.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, _, next) => {
    const token = localStorage.getItem('token')
    const publicPages = ['/login', '/register']
    const authRequired = !publicPages.includes(to.path)

    if (authRequired && !token) {
        return next('/login')
    }

    next()
})

export default router
