<template>
  <div class="visual-gallery animate-reveal-up">
    <!-- Gallery Header -->
    <header class="gallery-header">
       <div class="header-main">
          <h2 class="gallery-title">品牌视觉馆</h2>
          <p class="gallery-subtitle">管理并自定义文章的 CSS 视觉样式，打造独特的品牌感知。</p>
       </div>
       <n-button type="primary" size="large" round @click="showCreateModal = true" class="shadow-primary">
          <template #icon><n-icon :component="Plus" /></template>
          创作新视觉方案
       </n-button>
    </header>

    <!-- Gallery Search & Filter (Concept) -->
    <div class="gallery-filters glass-panel">
       <div class="filter-group">
          <n-button quaternary round size="small">全部</n-button>
          <n-button quaternary round size="small">官方预设</n-button>
          <n-button quaternary round size="small">我的自定义</n-button>
       </div>
    </div>

    <!-- Styles Grid -->
    <div class="gallery-grid">
      <div
        v-for="style in styles"
        :key="style.id"
        class="visual-card bento-card"
        @click="viewStyle(style)"
      >
        <div class="card-visual" :style="{ background: style.is_system ? 'var(--primary-gradient)' : 'var(--accent-gradient)' }">
           <n-icon :component="Palette" :size="40" color="rgba(255,255,255,0.8)" />
           <div v-if="style.is_system" class="official-tag">Official</div>
        </div>

        <div class="card-content">
          <div class="content-main">
             <h3 class="v-name">{{ style.name }}</h3>
             <p class="v-desc">{{ style.description || '精心设计的文章排版视觉方案。' }}</p>
          </div>
          
          <div class="card-actions-row">
             <div class="actions-left">
                <n-button text circle @click.stop="viewStyle(style)">
                   <template #icon><n-icon :component="Eye" /></template>
                </n-button>
                <n-button v-if="!style.is_system" text circle type="error" @click.stop="deleteStyle(style.id)">
                   <template #icon><n-icon :component="Trash2" /></template>
                </n-button>
             </div>
             <div class="actions-right">
                <n-tag size="tiny" :bordered="false" round>CSS v1.0</n-tag>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal (Premium Style) -->
    <n-modal 
      v-model:show="showCreateModal" 
      preset="card" 
      title="配置新视觉方案" 
      style="width: 700px; border-radius: var(--radius-xl);"
      class="visual-modal"
    >
      <n-form
        ref="createFormRef"
        :model="createModel"
        :rules="createRules"
        label-placement="top"
        require-mark-placement="right-hanging"
      >
        <div class="modal-grid">
           <div class="m-col">
              <n-form-item label="核心名称" path="name">
                <n-input v-model:value="createModel.name" placeholder="例如：未来主义极简主义" />
              </n-form-item>
              
              <n-form-item label="方案描述" path="description">
                <n-input
                  v-model:value="createModel.description"
                  type="textarea"
                  placeholder="简要说明此样式的适用场景..."
                />
              </n-form-item>
              
              <n-form-item label="生成引擎指令 (Prompt)" path="prompt_instruction">
                <n-input
                  v-model:value="createModel.prompt_instruction"
                  type="textarea"
                  :rows="4"
                  placeholder="告诉 AI 应该以何种语气和结构写作..."
                />
              </n-form-item>
           </div>

           <div class="m-col">
              <n-form-item label="选择基础底稿" path="preset">
                 <n-select
                    v-model:value="selectedPreset"
                    :options="PRESET_STYLES"
                    @update:value="handlePresetChange"
                 />
              </n-form-item>

              <n-form-item label="CSS 代码实验室">
                <n-input
                  v-model:value="createModel.css_content"
                  type="textarea"
                  :rows="10"
                  placeholder="/* 自定义您的 CSS 代码 */"
                  class="code-textarea"
                />
              </n-form-item>
           </div>
        </div>
        
        <template #footer>
           <div class="modal-footer-btns">
              <n-button secondary round @click="showCreateModal = false">放弃修改</n-button>
              <n-button type="primary" round class="shadow-primary" @click="handleCreateStyle">保存视觉方案</n-button>
           </div>
        </template>
      </n-form>
    </n-modal>

    <!-- Preview Modal -->
    <n-modal 
      v-model:show="showPreviewModal" 
      preset="card" 
      title="视觉方案预览" 
      style="width: 600px; border-radius: var(--radius-xl);"
    >
      <div v-if="previewStyle" class="preview-details">
        <div class="p-header">
           <div class="p-icon" :style="{ background: previewStyle.is_system ? 'var(--primary-gradient)' : 'var(--accent-gradient)' }">
              <n-icon :component="Palette" :size="32" color="white" />
           </div>
           <div class="p-meta">
              <h3>{{ previewStyle.name }}</h3>
              <p>{{ previewStyle.description }}</p>
           </div>
        </div>
        <n-divider title-placement="left">AI 指令细节</n-divider>
        <div class="p-prompt">
          <pre>{{ previewStyle.prompt_instruction || '未配置特定写作指令' }}</pre>
        </div>
        <n-divider title-placement="left">CSS 核心代码</n-divider>
        <div class="p-code">
           <pre>{{ previewStyle.css_content || '/* 无 CSS 内容 */' }}</pre>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  useMessage, NButton, NIcon, NModal, NForm, NFormItem, 
  NInput, NSelect, NSwitch, NCollapseTransition, NTag, NDivider 
} from 'naive-ui'
import { Palette, Plus, Eye, Trash2, Search, Filter } from 'lucide-vue-next'
import { styleApi, type Style, type StyleCreate } from '@/api/style'

// 预设样式
const PRESET_STYLES = [
  {
    label: '极简主义 (默认)',
    value: 'simple-white',
    css: `/* 极简主义风格 */\nbody {\n    font-family: 'Outfit', sans-serif;\n    color: #0f172a;\n    line-height: 1.8;\n}`
  },
  {
    label: '深邃暗色',
    value: 'geek-dark',
    css: `/* 深邃暗色风格 */\nbody {\n    background-color: #0b0f1a;\n    color: #f8fafc;\n}`
  },
  {
    label: '品牌 Indigo',
    value: 'business-blue',
    css: `/* 品牌 Indigo 风格 */\nbody {\n    color: #1e293b;\n}\nh1 {\n    color: #6366f1;\n}`
  }
]

const message = useMessage()
const styles = ref<Style[]>([])
const showCreateModal = ref(false)
const showPreviewModal = ref(false)
const previewStyle = ref<Style | null>(null)

// Form states
const createFormRef = ref()
const selectedPreset = ref('simple-white')

const createModel = ref<StyleCreate>({
  name: '',
  description: '',
  prompt_instruction: '',
  css_content: PRESET_STYLES[0].css
})

const createRules = {
  name: { required: true, message: '请输入视觉方案名称', trigger: 'blur' },
  description: { required: true, message: '请输入简单描述', trigger: 'blur' },
  prompt_instruction: { required: true, message: '请输入 AI 写作指令', trigger: 'blur' }
}

const handlePresetChange = (value: string) => {
  const preset = PRESET_STYLES.find(p => p.value === value)
  if (preset) createModel.value.css_content = preset.css
}

const fetchStyles = async () => {
  try {
    styles.value = await styleApi.getStyles()
  } catch (error) {
    message.error('视觉库同步失败')
  }
}

const handleCreateStyle = async () => {
  try {
    await createFormRef.value?.validate()
    await styleApi.createStyle(createModel.value)
    message.success('新视觉方案已入库')
    showCreateModal.value = false
    fetchStyles()
    createModel.value = { name: '', description: '', prompt_instruction: '', css_content: '' }
  } catch (error) {
    if (error instanceof Error) message.error(error.message)
  }
}

const viewStyle = (style: any) => {
  previewStyle.value = style
  showPreviewModal.value = true
}

const deleteStyle = async (id: number) => {
  try {
    await styleApi.deleteStyle(id)
    message.success('已从馆藏中移除')
    fetchStyles()
  } catch (error) {
    message.error('移除操作失败')
  }
}

onMounted(() => fetchStyles())
</script>

<style scoped>
.visual-gallery {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ========== GALLERY HEADER ========== */
.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gallery-title {
  font-size: 28px;
  font-weight: 900;
  color: var(--text-main);
  letter-spacing: -0.04em;
  margin-bottom: 4px;
}

.gallery-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 600;
}

/* ========== FILTERS ========== */
.gallery-filters {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  width: fit-content;
}

.filter-group {
  display: flex;
  gap: var(--spacing-xs);
}

/* ========== GRID & CARDS ========== */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.visual-card {
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.card-visual {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.official-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: 800;
  color: white;
  text-transform: uppercase;
}

.card-content {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  flex: 1;
}

.content-main {
  flex: 1;
  margin-bottom: var(--spacing-md);
}

.v-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 4px;
}

.v-desc {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.card-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.actions-left {
  display: flex;
  gap: var(--spacing-xs);
}

/* ========== MODAL STYLING ========== */
.modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

.code-textarea :deep(.n-input-wrapper) {
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  background: var(--bg-dark);
  color: #63eeff;
}

.modal-footer-btns {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  width: 100%;
}

/* PREVIEW DETAILS */
.preview-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.p-header {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
}

.p-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-prompt pre, .p-code pre {
  background: var(--bg-hover);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  font-family: inherit;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .modal-grid { grid-template-columns: 1fr; }
}
</style>
