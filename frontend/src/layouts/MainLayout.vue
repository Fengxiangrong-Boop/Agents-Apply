<template>
  <div class="app-container">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="logo-section">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <span class="logo-text">WeChat Agent</span>
      </div>

      <nav class="sidebar-nav">
        <n-menu
          :collapsed-width="64"
          :collapsed-icon-size="20"
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleUpdateValue"
          class="sidebar-menu"
        />
      </nav>
    </aside>

    <!-- 右侧主体 -->
    <main class="main-content">
      <!-- 顶部Header -->
      <header class="top-header">
        <h1 class="page-title">{{ currentTitle }}</h1>
        <div class="header-actions">
          <n-dropdown :options="userOptions" @select="handleUserSelect">
            <n-button text class="user-button">
              <n-avatar :size="32" round class="user-avatar">
                {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
              </n-avatar>
              <span class="username">{{ authStore.user?.username || '用户' }}</span>
              <n-icon :component="ChevronDown" :size="14" />
            </n-button>
          </n-dropdown>
        </div>
      </header>

      <!-- 内容滚动区域 -->
      <div class="content-scrollable">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { NMenu, NIcon, NDropdown, NButton, NAvatar } from 'naive-ui'
import { Home, PenTool, Settings, LogOut, Image, ChevronDown } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeKey = computed(() => route.name as string)

const titleMap: Record<string, string> = {
  'Dashboard': '工作台',
  'Articles': '文章创作',
  'Styles': '样式库',
  'Settings': '系统设置'
}

const currentTitle = computed(() => titleMap[activeKey.value] || '工作台')

const menuOptions = [
  {
    label: () => h(RouterLink, { to: { name: 'Dashboard' } }, { default: () => '工作台' }),
    key: 'Dashboard',
    icon: () => h(NIcon, { component: Home })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Articles' } }, { default: () => '文章创作' }),
    key: 'Articles',
    icon: () => h(NIcon, { component: PenTool })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Styles' } }, { default: () => '样式库' }),
    key: 'Styles',
    icon: () => h(NIcon, { component: Image })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Settings' } }, { default: () => '系统设置' }),
    key: 'Settings',
    icon: () => h(NIcon, { component: Settings })
  }
]

const userOptions = [
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, { component: LogOut })
  }
]

const handleUpdateValue = () => {
  // 路由已通过RouterLink处理
}

const handleUserSelect = (key: string) => {
  if (key === 'logout') {
    authStore.clearToken()
    router.push({ name: 'Login' })
  }
}
</script>

<style scoped>
/* ========== 容器布局 ========== */
.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 200px;
  height: 100%;
  background-color: var(--sidebar-bg);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.logo-section {
  padding: var(--spacing-lg) var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-lg) var(--spacing-md);
  overflow-y: auto;
}

/* 菜单样式 */
.sidebar-menu {
  background: transparent !important;
}

.sidebar-menu :deep(.n-menu-item) {
  color: #FFFFFF !important;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  height: 40px;
  font-size: 14px;
  position: relative;
  font-weight: 500;
}

.sidebar-menu :deep(.n-menu-item::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  border-radius: 0 2px 2px 0;
  transition: background var(--transition-fast);
}

.sidebar-menu :deep(.n-menu-item:hover) {
  background: rgba(148, 163, 184, 0.1) !important;
  color: #FFFFFF !important;
}

.sidebar-menu :deep(.n-menu-item.n-menu-item--selected) {
  background: rgba(16, 185, 129, 0.2) !important;
  color: #FFFFFF !important;
  font-weight: 600;
}

.sidebar-menu :deep(.n-menu-item.n-menu-item--selected::before) {
  background: var(--sidebar-active-border);
}

.sidebar-menu :deep(.n-menu-item-content-header) {
  color: inherit !important;
}

.sidebar-menu :deep(.n-icon) {
  color: inherit !important;
}

.sidebar-menu :deep(.n-menu-item-content__icon) {
  color: #FFFFFF !important;
}

.sidebar-menu :deep(a) {
  color: #FFFFFF !important;
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  min-width: 0;
}

.top-header {
  height: 56px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 0 var(--spacing-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.user-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  transition: background var(--transition-fast);
}

.user-button:hover {
  background: var(--bg-hover);
}

.user-avatar {
  background: var(--primary-gradient);
  color: white;
  font-weight: 600;
  font-size: 13px;
}

.username {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.content-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl);
}

/* 滚动条样式 */
.content-scrollable::-webkit-scrollbar,
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.content-scrollable::-webkit-scrollbar-track,
.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.content-scrollable::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: var(--radius-full);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
}

.content-scrollable::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
