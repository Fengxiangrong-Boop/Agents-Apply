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

    <!-- 创建样式模态框 -->
    <n-modal v-model:show="showCreateModal" preset="card" title="创建新样式" style="width: 600px;">
      <n-form
        ref="createFormRef"
        :model="createModel"
        :rules="createRules"
        label-placement="left"
        label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="样式名称" path="name">
          <n-input v-model:value="createModel.name" placeholder="例如：科技极客风格" />
        </n-form-item>
        
        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="createModel.description"
            type="textarea"
            placeholder="简要描述该样式的特点，例如：适合科技、技术类文章..."
          />
        </n-form-item>
        
        <n-form-item label="Prompt指令" path="prompt_instruction">
          <n-input
            v-model:value="createModel.prompt_instruction"
            type="textarea"
            :rows="5"
            placeholder="示例：请使用轻松幽默的口语化风格写作。
1. 多用感叹号和emoji表情 😊
2. 像在和朋友聊天一样自然
3. 避免使用过于严肃或学术的词汇"
          />
        </n-form-item>
        
        <n-form-item label="视觉主题" path="preset">
           <n-select
              v-model:value="selectedPreset"
              :options="PRESET_STYLES"
              @update:value="handlePresetChange"
           />
        </n-form-item>

        <n-form-item label="高级配置">
           <n-switch v-model:value="showAdvancedCss">
              <template #checked>自定义CSS</template>
              <template #unchecked>使用预设</template>
           </n-switch>
        </n-form-item>

        <n-collapse-transition :show="showAdvancedCss">
          <n-form-item label="CSS样式" path="css_content">
            <n-input
              v-model:value="createModel.css_content"
              type="textarea"
              :rows="8"
              placeholder="示例：
  /* 设置正文字体和颜色 */
  body {
      font-family: '微软雅黑', sans-serif;
      color: #333;
      line-height: 1.6;
  }
  
  /* 设置标题样式 */
  h1 {
      color: #ff6b6b; /* 红色标题 */
      border-bottom: 2px solid #ff6b6b;
      padding-bottom: 10px;
  }"
              font-family="monospace"
            />
          </n-form-item>
        </n-collapse-transition>
        
        <div class="form-actions" style="display: flex; justify-content: flex-end; gap: 12px;">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateStyle">创建</n-button>
        </div>
      </n-form>
    </n-modal>

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
import { 
  useMessage, NButton, NIcon, NModal, NForm, NFormItem, 
  NInput, NSelect, NSwitch, NCollapseTransition 
} from 'naive-ui'
import { Palette, Plus, Eye, Trash2 } from 'lucide-vue-next'
import { styleApi, type Style, type StyleCreate } from '@/api/style'

// 预设样式
const PRESET_STYLES = [
  {
    label: '简约白 (默认)',
    value: 'simple-white',
    css: `/* 简约白风格 */
body {
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: #333;
    line-height: 1.8;
    background-color: #fff;
    padding: 20px;
}
h1 {
    font-size: 24px;
    font-weight: bold;
    color: #000;
    margin-bottom: 20px;
}
h2 {
    font-size: 20px;
    font-weight: bold;
    color: #333;
    margin-top: 24px;
    margin-bottom: 16px;
    border-left: 4px solid #333;
    padding-left: 10px;
}
p {
    margin-bottom: 16px;
    text-align: justify;
}
strong {
    color: #000;
    font-weight: bold;
}
blockquote {
    background: #f5f5f5;
    border-left: 4px solid #ccc;
    padding: 10px 15px;
    margin: 15px 0;
    color: #666;
}`
  },
  {
    label: '商务蓝',
    value: 'business-blue',
    css: `/* 商务蓝风格 */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #2c3e50;
    line-height: 1.75;
}
h1 {
    color: #1a5cff;
    border-bottom: 1px solid #eaeaea;
    padding-bottom: 15px;
}
h2 {
    color: #1a5cff;
    background: #f0f7ff;
    padding: 8px 12px;
    border-radius: 4px;
    border-left: 4px solid #1a5cff;
}
strong {
    color: #1a5cff;
}
ul li {
    list-style-type: square;
    color: #4a5568;
}`
  },
  {
    label: '温馨暖色',
    value: 'warm-orange',
    css: `/* 温馨暖色风格 */
body {
    font-family: 'Optima', sans-serif;
    color: #5d4037;
    background-color: #fffaf0;
}
h1 {
    color: #ff7043;
    text-align: center;
}
h2 {
    color: #f4511e;
    border-bottom: 2px dashed #ffab91;
    padding-bottom: 5px;
    display: inline-block;
}
p {
    margin-bottom: 18px;
}
strong {
    color: #d84315;
    background: linear-gradient(120deg, #ffccbc 0%, #ffccbc 100%);
    background-repeat: no-repeat;
    background-size: 100% 40%;
    background-position: 0 88%;
}`
  },
  {
    label: '极客黑',
    value: 'geek-dark',
    css: `/* 极客黑风格 */
body {
    font-family: 'Fira Code', monospace;
    color: #e0e0e0;
    background-color: #1e1e1e;
    padding: 20px;
}
h1 {
    color: #4ec9b0;
    text-shadow: 0 0 5px rgba(78, 201, 176, 0.3);
}
h2 {
    color: #569cd6;
    margin-top: 30px;
}
code {
    background: #2d2d2d;
    padding: 2px 5px;
    border-radius: 3px;
    color: #ce9178;
}
blockquote {
    border-left: 3px solid #6a9955;
    color: #6a9955;
    padding-left: 10px;
}`
  }
]

const message = useMessage()
const styles = ref<Style[]>([])
const showCreateModal = ref(false)
const showPreviewModal = ref(false)
const previewStyle = ref<Style | null>(null)

// Form states
const createFormRef = ref()
const showAdvancedCss = ref(false)
const selectedPreset = ref('simple-white')

const createModel = ref<StyleCreate>({
  name: '',
  description: '',
  prompt_instruction: '',
  css_content: PRESET_STYLES[0]?.css || '' // Default init
})

const createRules = {
  name: {
    required: true,
    message: '请输入样式名称',
    trigger: 'blur'
  },
  description: {
    required: true,
    message: '请输入样式描述',
    trigger: 'blur'
  },
  prompt_instruction: {
    required: true,
    message: '请输入Prompt指令',
    trigger: 'blur'
  },
  css_content: {
    required: true,
    message: '请输入CSS样式',
    trigger: 'blur'
  }
}

// Update CSS when preset changes
const handlePresetChange = (value: string) => {
  const preset = PRESET_STYLES.find(p => p.value === value)
  if (preset) {
    createModel.value.css_content = preset.css
  }
}

const fetchStyles = async () => {
  try {
    styles.value = await styleApi.getStyles()
  } catch (error) {
    message.error('获取样式列表失败')
  }
}

const handleCreateStyle = async () => {
  try {
    await createFormRef.value?.validate()
    await styleApi.createStyle(createModel.value)
    message.success('创建成功')
    showCreateModal.value = false
    fetchStyles()
    // Reset form
    createModel.value = {
      name: '',
      description: '',
      prompt_instruction: '',
      css_content: ''
    }
  } catch (error) {
    // Validation error or API error
    if (error instanceof Error) {
       message.error(error.message || '创建失败')
    }
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
