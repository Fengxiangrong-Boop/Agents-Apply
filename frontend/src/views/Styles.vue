<template>
  <div class="styles-page">
    <div class="page-header">
      <h2>样式库</h2>
      <n-button type="primary" @click="showCreateModal = true" class="create-button">
        <template #icon>
          <n-icon :component="Plus" />
        </template>
        创建样式
      </n-button>
    </div>

    <!-- 样式卡片Grid -->
    <div class="styles-grid">
      <div
        v-for="style in styles"
        :key="style.id"
        class="style-card shadow-hover"
      >
        <div class="card-header">
          <div class="style-preview">
            <n-icon :component="Palette" :size="32" />
          </div>
          <div v-if="style.is_system" class="system-badge">官方</div>
        </div>

        <div class="card-body">
          <h3 class="style-name">{{ style.name }}</h3>
          <p class="style-description">{{ style.description || '暂无描述' }}</p>
        </div>

        <div class="card-footer">
          <n-button text type="primary" @click="viewStyle(style)">
            <n-icon :component="Eye" />
            预览
          </n-button>
          <n-button v-if="!style.is_system" text type="error" @click="deleteStyle(style.id)">
            <n-icon :component="Trash2" />
            删除
          </n-button>
        </div>
      </div>
    </div>

    <!-- 预览模态框 -->
    <n-modal v-model:show="showPreviewModal" preset="card" :title="previewStyle?.name" style="width: 600px;">
      <div v-if="previewStyle">
        <p><strong>描述：</strong>{{ previewStyle.description }}</p>
        <div class="prompt-preview">
          <strong>Prompt：</strong>
          <pre>{{ previewStyle.prompt_instruction || '无' }}</pre>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage, NButton, NIcon, NModal } from 'naive-ui'
import { Palette, Plus, Eye, Trash2 } from 'lucide-vue-next'
import { styleApi, type Style } from '@/api/style'

const message = useMessage()
const styles = ref<Style[]>([])
const showCreateModal = ref(false)
const showPreviewModal = ref(false)
const previewStyle = ref<Style | null>(null)

const fetchStyles = async () => {
  try {
    styles.value = await styleApi.getStyles()
  } catch (error) {
    message.error('获取样式列表失败')
  }
}

const viewStyle = (style: any) => {
  previewStyle.value = style
  showPreviewModal.value = true
}

const deleteStyle = async (id: number) => {
  try {
    await styleApi.deleteStyle(id)
    message.success('删除成功')
    fetchStyles()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchStyles()
})
</script>

<style scoped>
.styles-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.create-button {
  background: var(--primary-gradient);
  border: none;
  font-weight: 600;
}

/* ========== 样式Grid ========== */
.styles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.style-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.style-card:hover {
  transform: translateY(-4px);
}

.card-header {
  position: relative;
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg) 0;
}

.style-preview {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-md);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.system-badge {
  position: absolute;
  top: 0;
  right: 0;
  padding: 4px 12px;
  background: var(--success-color);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-sm);
}

.card-body {
  flex: 1;
  text-align: center;
}

.style-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs);
}

.style-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
}

.prompt-preview {
  margin-top: var(--spacing-md);
}

.prompt-preview pre {
  background: var(--bg-base);
  padding: var(--spacing-md);
  border-radius: var(--radius-sm);
  font-size: 12px;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .styles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
