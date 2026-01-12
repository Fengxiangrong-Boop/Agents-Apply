<template>
  <div class="articles-page">
    <n-card title="文章创作" class="create-card">
      <div class="create-form">
        <!-- 主题输入 -->
        <div class="form-section">
          <label class="form-label">文章主题</label>
          <n-input
            v-model:value="theme"
            size="large"
            placeholder="请输入文章主题，例如：人工智能的未来发展"
            class="theme-input"
          />
        </div>

        <!-- 样式选择 -->
        <div class="form-section">
          <label class="form-label">选择样式</label>
          <div class="styles-grid">
            <div
              v-for="style in styles"
              :key="style.id"
              class="style-card"
              :class="{ active: selectedStyleId === style.id }"
              @click="selectedStyleId = style.id"
            >
              <div class="style-icon">
                <n-icon :component="Palette" :size="24" />
              </div>
              <div class="style-name">{{ style.name }}</div>
              <div v-if="style.is_system" class="style-badge">官方</div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions">
          <n-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="!theme || !selectedStyleId"
            @click="handleGenerate"
            class="generate-button"
          >
            <template #icon>
              <n-icon :component="Sparkles" />
            </template>
            生成文章
          </n-button>

          <n-button
            v-if="currentArticle"
            secondary
            size="large"
            :loading="syncing"
            @click="handleSync"
            class="sync-button"
          >
            <template #icon>
              <n-icon :component="Send" />
            </template>
            同步到微信
          </n-button>
        </div>
      </div>
    </n-card>

    <!-- 预览区域 -->
    <n-card v-if="currentArticle" title="预览" class="preview-card">
      <div class="preview-content" v-html="currentArticle.content_html"></div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage, NCard, NInput, NButton, NIcon } from 'naive-ui'
import { Palette, Sparkles, Send } from 'lucide-vue-next'
import { articleApi, type Style } from '@/api/article'
import { styleApi } from '@/api/style'

const message = useMessage()
const route = useRoute()
const theme = ref('')
const styles = ref<Style[]>([])
const selectedStyleId = ref<number | null>(null)
const generating = ref(false)
const syncing = ref(false)
const currentArticle = ref<any>(null)

const fetchStyles = async () => {
  try {
    styles.value = await styleApi.getStyles()
    if (styles.value.length > 0 && !selectedStyleId.value) {
      selectedStyleId.value = styles.value[0]?.id || null
    }
  } catch (error) {
    message.error('获取样式失败')
  }
}

const fetchArticle = async (id: number) => {
  try {
    const article = await articleApi.getArticle(id)
    currentArticle.value = article
    theme.value = article.prompt_input
    // If we have style info in article (currently not in interface but good to handle if added), set it here
  } catch (error) {
    message.error('获取文章详情失败')
  }
}

const handleGenerate = async () => {
  if (!theme.value || !selectedStyleId.value) return

  generating.value = true
  try {
    const article = await articleApi.createArticle({
      prompt_input: theme.value,
      style_id: selectedStyleId.value
    })
    currentArticle.value = article
    message.success('文章生成成功')
  } catch (error: any) {
    message.error('生成失败：' + (error.response?.data?.detail || '请稍后重试'))
  } finally {
    generating.value = false
  }
}

const handleSync = async () => {
  if (!currentArticle.value) return

  syncing.value = true
  try {
    await articleApi.syncArticle(currentArticle.value.id)
    message.success('同步成功')
    currentArticle.value.synced_at = new Date().toISOString()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '同步失败'
    message.error(errorMsg)
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchStyles()
  const id = route.query.id
  if (id) {
    fetchArticle(Number(id))
  }
})

// Listen to route changes (in case of navigation within same component)
watch(() => route.query.id, (newId) => {
  if (newId) {
    fetchArticle(Number(newId))
  } else {
    currentArticle.value = null
    theme.value = ''
  }
})
</script>

<style scoped>
.articles-page {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

/* ========== 创作卡片 ========== */
.create-card {
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-md);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-input {
  font-size: 16px;
}

/* ========== 样式选择 ========== */
.styles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--spacing-md);
}

.style-card {
  position: relative;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
}

.style-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.style-card.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.style-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-sm);
  border-radius: var(--radius-md);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.style-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.style-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  background: var(--primary-color);
  color: white;
  font-size: 12px;
  border-radius: var(--radius-sm);
}

/* ========== 操作按钮 ========== */
.actions {
  display: flex;
  gap: var(--spacing-md);
}

.generate-button, .sync-button {
  flex: 1;
  font-weight: 600;
}

.generate-button {
  background: var(--primary-gradient);
  border: none;
}

.generate-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* ========== 预览卡片 ========== */
.preview-card {
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-md);
}

.preview-content {
  padding: var(--spacing-lg);
  background: var(--bg-base);
  border-radius: var(--radius-sm);
  max-height: 600px;
  overflow-y: auto;
}

.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3) {
  color: var(--text-primary);
}

.preview-content :deep(p) {
  color: var(--text-secondary);
  line-height: 1.8;
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .articles-page {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .styles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>
