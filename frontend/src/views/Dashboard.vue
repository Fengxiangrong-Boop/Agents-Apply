<template>
  <div class="dashboard-root animate-reveal-up">
    <!-- HERO SECTION -->
    <header class="hero-section">
      <div class="hero-left">
        <h1 class="welcome-title">早安, <span class="text-gradient">{{ authStore.user?.username || '创造者' }}</span> ✨</h1>
        <p class="hero-subtitle">欢迎回到 AI 微信创作助手。您在本周已生成了 12 篇内容，击败了 85% 的创作者。</p>
      </div>
      <div class="hero-right">
        <n-button type="primary" size="large" round @click="router.push({ name: 'Articles' })" class="cta-pulse shadow-primary">
          <template #icon><n-icon :component="PenTool" /></template>
          开启今日灵感
        </n-button>
      </div>
    </header>

    <!-- KEY METRICS GRID -->
    <section class="metrics-row">
      <div v-for="stat in stats" :key="stat.label" class="metric-bento glass-panel">
        <div class="metric-icon" :style="{ background: stat.bgColor }">
          <n-icon :component="stat.icon" :size="20" :style="{ color: stat.color }" />
        </div>
        <div class="metric-info">
          <span class="m-label">{{ stat.label }}</span>
          <div class="m-stats">
            <span class="m-value font-heading">{{ stat.value }}</span>
            <span class="m-trend" :class="stat.trend > 0 ? 'pos' : 'neg'">
              <n-icon :component="stat.trend > 0 ? TrendingUp : TrendingDown" :size="12" />
              {{ Math.abs(stat.trend) }}%
            </span>
          </div>
        </div>
        <!-- Abstract sparkline decoration -->
        <svg class="m-graph" viewBox="0 0 100 30">
          <path :d="stat.path" fill="none" :stroke="stat.color" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
    </section>

    <!-- MAIN BENTO CONTENT AREA -->
    <div class="dashboard-bento-grid">
      <!-- Recent Content (Main Bento) -->
      <n-card :bordered="false" class="bento-col-span-2 main-content-bento">
        <template #header>
          <div class="bento-header">
            <div class="b-title">
               <n-icon :component="History" :size="20" />
               最近创作成果
            </div>
            <n-button text type="primary" size="small" @click="router.push({ name: 'Articles' })">管理全部</n-button>
          </div>
        </template>
        
        <n-data-table
          :columns="columns"
          :data="articles"
          :pagination="false"
          :bordered="false"
          :loading="loading"
          class="premium-table"
        />
        
        <div v-if="articles.length === 0 && !loading" class="empty-placeholder">
           <n-empty description="在这里开始您的第一篇 AI 创作" />
        </div>
      </n-card>

      <!-- Sidebar Bento Widgets -->
      <div class="bento-sidebar">
        <!-- Inspiration Widget -->
        <n-card :bordered="false" class="widget-card-pro gradient-widget">
           <div class="widget-inner">
              <span class="w-tag">今日灵感推荐</span>
              <h3 class="w-title">如何利用 AI 打造品牌视觉差异化？</h3>
              <p class="w-desc">掌握 prompt 调优的核心逻辑，让您的文章脱颖而出。</p>
              <n-button size="small" round secondary class="w-btn">立即阅读</n-button>
           </div>
        </n-card>

        <!-- System Status Bento -->
        <n-card :bordered="false" class="widget-card-pro status-bento">
           <div class="status-bento-header">
              <span class="h-text">系统运行状态</span>
              <div class="h-dot glow-pulse"></div>
           </div>
           <div class="status-items">
              <div class="s-item">
                 <span class="s-label">核心生成引擎</span>
                 <n-tag size="small" :bordered="false" type="success" round>Active</n-tag>
              </div>
              <div class="s-item">
                 <span class="s-label">微信接口同步</span>
                 <n-tag size="small" :bordered="false" type="info" round>Standby</n-tag>
              </div>
           </div>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NCard, NDataTable, NTag, NButton, NIcon, 
  NEmpty, NAvatar, NSpace, NProgress 
} from 'naive-ui'
import { 
  FileText, CheckCircle, Clock, Plus, TrendingUp, TrendingDown, 
  LayoutDashboard, FileEdit, Share2, History, PenTool, Zap
} from 'lucide-vue-next'
import { articleApi, type Article } from '@/api/article'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const articles = ref<Article[]>([])
const loading = ref(false)

// Generate some fake sparkline paths for decoration
const paths = [
  "M 0 20 Q 25 10 50 20 T 100 10",
  "M 0 10 Q 30 25 60 10 T 100 20",
  "M 0 15 Q 20 25 40 15 T 70 25 T 100 10"
]

const stats = computed(() => {
  const total = articles.value.length
  const synced = articles.value.filter((a: any) => a.synced_at).length
  const draft = total - synced

  return [
    {
      label: '创作总量',
      value: total,
      icon: FileEdit,
      color: '#6366F1',
      bgColor: 'rgba(99, 102, 241, 0.1)',
      trend: 12,
      path: paths[0]
    },
    {
      label: '已发布',
      value: synced,
      icon: Share2,
      color: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      trend: 8,
      path: paths[1]
    },
    {
      label: '待优化草稿',
      value: draft,
      icon: Clock,
      color: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      trend: -3,
      path: paths[2]
    }
  ]
})

const columns = [
  {
    title: '文章主题与 ID',
    key: 'title',
    render(row: any) {
      return h('div', { class: 'article-meta-cell' }, [
        h('div', { class: 'meta-title' }, row.title),
        h('div', { class: 'meta-subtitle' }, `Content Hash: ${row.id.toString().padEnd(8, '0')} · Revised 2h ago`)
      ])
    }
  },
  {
    title: '同步状态',
    key: 'synced_at',
    width: 140,
    render(row: any) {
      return h(NTag, {
        type: row.synced_at ? 'success' : 'info',
        size: 'small',
        round: true,
        strong: true,
        bordered: false,
        style: { padding: '2px 12px' }
      }, { 
        default: () => [
          h(NIcon, { component: row.synced_at ? CheckCircle : Clock, size: 14, style: { marginRight: '4px' } }),
          row.synced_at ? '已同步' : '编辑中'
        ]
      })
    }
  },
  {
    title: '交互',
    key: 'actions',
    width: 120,
    render(row: any) {
      return h(NButton, {
        secondary: true,
        round: true,
        type: 'primary',
        size: 'small',
        onClick: () => router.push({ name: 'Articles', query: { id: row.id.toString() } })
      }, { default: () => '工作台管理' })
    }
  }
]

const fetchArticles = async () => {
  loading.value = true
  try {
    const data = await articleApi.getArticles()
    articles.value = data.slice(0, 8) 
  } catch (error) {
    console.error('获取基础数据失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.dashboard-root {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ========== HERO SECTION ========== */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-md);
}

.welcome-title {
  font-size: 32px;
  font-weight: 900;
  color: var(--text-main);
  margin-bottom: var(--spacing-2xs);
  letter-spacing: -0.04em;
}

.hero-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 600;
  max-width: 600px;
}

.cta-pulse {
  height: 52px !important;
  padding: 0 var(--spacing-xl) !important;
  font-weight: 800 !important;
  font-size: 15px !important;
}

/* ========== METRICS ROW (GLASS) ========== */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.metric-bento {
  padding: var(--spacing-lg);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
  border: 1px solid var(--border-color);
}

.metric-bento:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-hover);
}

.metric-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-info {
  flex: 1;
}

.m-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.m-stats {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-sm);
}

.m-value {
  font-size: 32px;
  font-weight: 900;
  color: var(--text-main);
}

.m-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.m-trend.pos { background: var(--success-glow); color: var(--success-color); }
.m-trend.neg { background: var(--accent-soft); color: var(--accent-color); }

.m-graph {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 120px;
  opacity: 0.3;
}

/* ========== BENTO GRID LAYOUT ========== */
.dashboard-bento-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--spacing-lg);
}

.main-content-bento {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  min-height: 500px;
}

.bento-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.b-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Table Style Overrides */
.premium-table :deep(.n-data-table-th) {
  background: var(--bg-hover);
  color: var(--text-tertiary);
  font-weight: 800;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: var(--spacing-md) var(--spacing-lg);
}

.premium-table :deep(.n-data-table-td) {
  padding: var(--spacing-md) var(--spacing-lg);
}

.article-meta-cell {
  display: flex;
  flex-direction: column;
}

.meta-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-main);
}

.meta-subtitle {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
}

/* Sidebar Widgets */
.bento-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.widget-card-pro {
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
}

.gradient-widget {
  background: var(--primary-gradient);
  color: white;
  border: none !important;
}

.widget-inner {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.w-tag {
  font-size: 10px;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.2);
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  width: fit-content;
  text-transform: uppercase;
}

.w-title {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.3;
}

.w-desc {
  font-size: 13px;
  opacity: 0.8;
  font-weight: 500;
}

.w-btn {
  width: fit-content;
  background: white !important;
  color: var(--primary-color) !important;
  font-weight: 800 !important;
  border: none !important;
  margin-top: var(--spacing-xs);
}

.status-bento-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.h-text {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
}

.h-dot {
  width: 8px;
  height: 8px;
  background: var(--success-color);
  border-radius: var(--radius-full);
}

.status-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.s-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-hover);
  border-radius: var(--radius-md);
}

.s-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
}

@media (max-width: 1200px) {
  .dashboard-bento-grid {
    grid-template-columns: 1fr;
  }
}
</style>
