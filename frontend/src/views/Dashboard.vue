<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div 
        v-for="(stat, index) in stats" 
        :key="index" 
        class="stat-card"
        :style="{ background: stat.gradient }"
      >
        <div class="stat-icon">
          <n-icon :component="stat.icon" :size="32" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div v-if="stat.trend" class="stat-trend" :class="stat.trend > 0 ? 'positive' : 'negative'">
          <n-icon :component="stat.trend > 0 ? TrendingUp : TrendingDown" :size="16" />
          {{ Math.abs(stat.trend) }}%
        </div>
      </div>
    </div>

    <!-- 最近文章 -->
    <n-card title="最近文章" class="recent-articles-card">
      <n-data-table
        :columns="columns"
        :data="articles"
        :pagination="false"
        :bordered="false"
        class="articles-table"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NDataTable, NTag, NButton, NIcon } from 'naive-ui'
import { FileText, CheckCircle, Clock, TrendingUp, TrendingDown } from 'lucide-vue-next'
import { articleApi, type Article } from '@/api/article'

const router = useRouter()
const articles = ref<Article[]>([])
const loading = ref(false)

// 统计数据
const stats = computed(() => {
  const total = articles.value.length
  const synced = articles.value.filter((a: any) => a.synced_at).length
  const draft = total - synced

  return [
    {
      label: '总文章数',
      value: total,
      icon: FileText,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: 12
    },
    {
      label: '已同步',
      value: synced,
      icon: CheckCircle,
      gradient: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
      trend: 8
    },
    {
      label: '草稿',
      value: draft,
      icon: Clock,
      gradient: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
      trend: -3
    }
  ]
})

// 表格列定义
const columns = [
  {
    title: '标题',
    key: 'title',
    ellipsis: { tooltip: true }
  },
  {
    title: '状态',
    key: 'synced_at',
    width: 120,
    render(row: any) {
      return h(NTag, {
        type: row.synced_at ? 'success' : 'info',
        size: 'small',
        round: true
      }, { default: () => row.synced_at ? '已同步' : '草稿' })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render(row: any) {
      return new Date(row.created_at).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render(row: any) {
      return h(NButton, {
        text: true,
        type: 'primary',
        size: 'small',
        onClick: () => viewArticle(row.id)
      }, { default: () => '查看' })
    }
  }
]

const fetchArticles = async () => {
  loading.value = true
  try {
    const data = await articleApi.getArticles()
    articles.value = data.slice(0, 10) // 最近10篇
  } catch (error) {
    console.error('获取文章列表失败', error)
  } finally {
    loading.value = false
  }
}

const viewArticle = (_id?: number) => {
  router.push({ name: 'Articles' })
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stat-card {
  position: relative;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  color: white;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  overflow: hidden;
  min-height: 85px;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(30%, -30%);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 0;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.2);
  font-size: 11px;
  font-weight: 600;
}

.stat-trend.positive {
  color: #10B981;
  background: rgba(16, 185, 129, 0.2);
}

.stat-trend.negative {
  color: #EF4444;
  background: rgba(239, 68, 68, 0.2);
}

/* ========== 最近文章卡片 ========== */
.recent-articles-card {
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-md);
}

.recent-articles-card :deep(.n-card__header) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 表格样式优化 */
.articles-table :deep(.n-data-table-th) {
  background: var(--bg-base);
  font-weight: 600;
}

.articles-table :deep(.n-data-table-tr:hover) {
  background: var(--bg-base);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
