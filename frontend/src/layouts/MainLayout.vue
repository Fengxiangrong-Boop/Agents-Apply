<template>
  <div class="app-container">
    <!-- Premium Sidebar (Floating Design Concept) -->
    <aside class="sidebar animate-reveal-in">
      <div class="sidebar-inner">
        <div class="logo-section">
          <div class="logo-wrapper">
            <div class="logo-icon-container">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="2"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
          <div class="logo-content">
            <span class="logo-label">AI WECHAT</span>
            <span class="logo-brand">AGENT PRO</span>
          </div>
        </div>

        <nav class="sidebar-navigation">
          <n-menu
            :collapsed-width="64"
            :collapsed-icon-size="22"
            :options="menuOptions"
            :value="activeKey"
            class="premium-menu"
          />
        </nav>

        <div class="sidebar-bottom">
          <div class="storage-usage">
            <div class="usage-header">
              <span>云存储空间</span>
              <span>85%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 85%"></div>
            </div>
          </div>
          
          <div class="connection-status">
            <div class="status-dot glow-pulse"></div>
            <span>服务连接正常</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Flow -->
    <main class="main-flow">
      <!-- Universal Header (Floating Glass) -->
      <header class="universal-header glass-panel">
        <div class="header-left">
          <div class="breadcrumb-nav">
             <span class="breadcrumb-item">Workspace</span>
             <n-icon :component="ChevronRight" :size="12" />
             <span class="breadcrumb-item active">{{ currentTitle }}</span>
          </div>
        </div>
        
        <div class="header-center">
           <div class="universal-search">
              <n-icon :component="Search" :size="16" />
              <input type="text" placeholder="搜索文章、样式或指令..." />
              <div class="search-kbd">⌘ K</div>
           </div>
        </div>

        <div class="header-right">
          <n-space :size="20" align="center">
            <n-button text class="icon-btn">
               <n-badge :value="3" dot color="#6366F1">
                  <n-icon :component="Bell" :size="20" />
               </n-badge>
            </n-button>
            
            <n-dropdown :options="userOptions" @select="handleUserSelect" trigger="hover" placement="bottom-end">
              <div class="user-pill">
                <n-avatar :size="34" round class="premium-avatar">
                   {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
                </n-avatar>
                <div class="user-meta">
                   <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
                   <span class="user-tier">Premium Plan</span>
                </div>
                <n-icon :component="ChevronDown" :size="14" />
              </div>
            </n-dropdown>
          </n-space>
        </div>
      </header>

      <!-- Content Scrollable View -->
      <div class="view-scroll-area">
        <div class="view-container">
          <router-view v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { NMenu, NIcon, NDropdown, NButton, NAvatar, NSpace, NBadge } from 'naive-ui'
import { 
  LayoutDashboard, PenTool, LayoutTemplate, Settings, 
  LogOut, ChevronDown, Activity, ChevronRight, Search, Bell 
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeKey = computed(() => route.name as string)

const titleMap: Record<string, string> = {
  'Dashboard': '工作台预览',
  'Articles': '智能创作中心',
  'Styles': '品牌视觉馆',
  'Settings': '全局个性化配置'
}

const currentTitle = computed(() => titleMap[activeKey.value] || '工作台')

const menuOptions = [
  {
    label: () => h(RouterLink, { to: { name: 'Dashboard' } }, { default: () => '仪表盘' }),
    key: 'Dashboard',
    icon: () => h(NIcon, { component: LayoutDashboard })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Articles' } }, { default: () => '文章创作' }),
    key: 'Articles',
    icon: () => h(NIcon, { component: PenTool })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Styles' } }, { default: () => '样式库' }),
    key: 'Styles',
    icon: () => h(NIcon, { component: LayoutTemplate })
  },
  {
    label: () => h(RouterLink, { to: { name: 'Settings' } }, { default: () => '系统设置' }),
    key: 'Settings',
    icon: () => h(NIcon, { component: Settings })
  }
]

const userOptions = [
  {
    label: '个人资料',
    key: 'profile',
    icon: () => h(NIcon, { component: LayoutDashboard })
  },
  { label: '---', key: 'divider', type: 'divider' },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, { component: LogOut })
  }
]

const handleUserSelect = (key: string) => {
  if (key === 'logout') {
    authStore.clearToken()
    router.push({ name: 'Login' })
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: var(--bg-color);
  overflow: hidden;
}

/* ========== PREMIUM SIDEBAR (DEEP SPACE) ========== */
.sidebar {
  width: 260px;
  height: 100%;
  padding: var(--spacing-md);
  flex-shrink: 0;
  z-index: 100;
}

.sidebar-inner {
  height: 100%;
  background-color: var(--bg-dark);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  box-shadow: 10px 0 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.logo-section {
  padding: var(--spacing-xl) var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-wrapper {
  position: relative;
}

.logo-icon-container {
  width: 44px;
  height: 44px;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 16px var(--primary-glow);
}

.logo-content {
  display: flex;
  flex-direction: column;
}

.logo-label {
  font-size: 10px;
  font-weight: 800;
  color: var(--primary-hover);
  letter-spacing: 0.1em;
  line-height: 1;
  margin-bottom: 2px;
}

.logo-brand {
  font-size: 16px;
  font-weight: 900;
  color: #FFFFFF;
  letter-spacing: -0.01em;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.sidebar-navigation {
  flex: 1;
  padding: 0 var(--spacing-sm);
}

/* Premium Menu Customization */
.premium-menu {
  background: transparent !important;
}

.premium-menu :deep(.n-menu-item) {
  margin-bottom: var(--spacing-xs);
}

.premium-menu :deep(.n-menu-item-content) {
  border-radius: var(--radius-md) !important;
  height: 48px !important;
  padding: 0 var(--spacing-md) !important;
  transition: all var(--transition-base) var(--spring-easing) !important;
}

.premium-menu :deep(.n-menu-item-content:hover) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: white !important;
}

.premium-menu :deep(.n-menu-item-content--selected) {
  background: var(--primary-gradient) !important;
  box-shadow: 0 8px 16px var(--primary-glow) !important;
  color: white !important;
  transform: scale(1.02);
}

.premium-menu :deep(.n-menu-item-content-header) {
  font-weight: 700 !important;
  color: rgba(255, 255, 255, 0.6) !important;
}

.premium-menu :deep(.n-menu-item-content--selected .n-menu-item-content-header) {
  color: white !important;
}

.premium-menu :deep(.n-icon) {
  color: rgba(255, 255, 255, 0.4) !important;
}

.premium-menu :deep(.n-menu-item-content--selected .n-icon) {
  color: white !important;
}

.sidebar-bottom {
  padding: var(--spacing-xl) var(--spacing-md);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.storage-usage {
  background: rgba(255, 255, 255, 0.03);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
}

.usage-header {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-gradient);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
}

.status-dot {
  width: 6px;
  height: 6px;
  background: var(--success-color);
  border-radius: var(--radius-full);
}

/* ========== MAIN FLOW AREA ========== */
.main-flow {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.universal-header {
  height: 68px;
  margin: var(--spacing-md) var(--spacing-lg);
  padding: 0 var(--spacing-xl);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 50;
  box-shadow: var(--shadow-md);
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  font-weight: 700;
  color: var(--text-tertiary);
}

.breadcrumb-item.active {
  color: var(--text-main);
}

.header-center {
  flex: 1;
  max-width: 480px;
  margin: 0 var(--spacing-xl);
}

.universal-search {
  height: 40px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-md);
  gap: var(--spacing-sm);
  color: var(--text-tertiary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-base);
}

.universal-search:focus-within {
  background: white;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px var(--primary-soft);
}

.universal-search input {
  background: transparent;
  border: none;
  outline: none;
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.search-kbd {
  background: white;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--border-color);
  font-size: 10px;
  font-weight: 800;
}

.icon-btn {
  color: var(--text-secondary) !important;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--primary-soft);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-base);
}

.user-pill:hover {
  background: rgba(99, 102, 241, 0.15);
}

.premium-avatar {
  background: var(--primary-gradient);
  color: white;
  font-weight: 800;
  border: 2px solid white;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-main);
}

.user-tier {
  font-size: 10px;
  font-weight: 700;
  color: var(--primary-color);
  text-transform: uppercase;
}

.view-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md) var(--spacing-lg) var(--spacing-xl);
}

.view-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s var(--spring-easing);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}
</style>
