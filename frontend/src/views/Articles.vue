<template>
  <div class="studio-root animate-reveal-up">
    <!-- Studio Header -->
    <header class="studio-header">
       <div class="h-left">
          <n-button quaternary circle size="large" @click="handleBack">
             <template #icon><n-icon :component="ArrowLeft" /></template>
          </n-button>
          <div class="h-meta">
             <h2 class="studio-title">AI 内容实验室</h2>
             <p class="studio-subtitle">智能生成、排版与发布同步一体化工作流</p>
          </div>
       </div>
       <div class="h-right">
          <n-space :size="12">
             <n-button round secondary @click="theme = ''; currentArticle = null">
                清空草稿
             </n-button>
             <n-button 
               v-if="currentArticle" 
               type="success" 
               round 
               secondary 
               :loading="syncing"
               @click="handleSync"
             >
                <template #icon><n-icon :component="Send" /></template>
                推送到微信
             </n-button>
          </n-space>
       </div>
    </header>

    <div class="studio-content">
      <!-- CONTROL PANEL -->
      <section class="control-panel">
        <n-card :bordered="false" class="premium-card control-inner">
           <div class="form-group">
              <div class="label-row">
                 <span class="f-label">实验室创作指令</span>
                 <n-tag size="tiny" :bordered="false" round type="primary">GPT-4 Supported</n-tag>
              </div>
              <n-input
                v-model:value="theme"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="在此输入您的创作主题或核心观点，AI 将为您生成完整的微信公众号文章..."
                class="studio-textarea"
              />
              <div class="textarea-footer">
                 <span>建议输入 50 字以上以获得最佳效果</span>
                 <span>{{ theme.length }} / 2000</span>
              </div>
           </div>

           <div class="form-group">
              <div class="label-row">
                 <span class="f-label">视觉风格预设</span>
                 <n-button text type="primary" size="tiny">管理视觉馆</n-button>
              </div>
              <div class="studio-styles-grid">
                 <div
                   v-for="style in styles"
                   :key="style.id"
                   class="style-pill"
                   :class="{ active: selectedStyleId === style.id }"
                   @click="selectedStyleId = style.id"
                 >
                   <div class="pill-icon">
                      <n-icon :component="Sparkles" />
                   </div>
                   <div class="pill-name">{{ style.name }}</div>
                   <div v-if="selectedStyleId === style.id" class="active-dot"></div>
                 </div>
              </div>
           </div>

           <div class="control-footer">
              <n-button
                type="primary"
                block
                secondary
                round
                class="studio-btn-main"
                :loading="generating"
                :disabled="!theme || !selectedStyleId"
                @click="handleGenerate"
              >
                <template #icon><n-icon :component="Zap" /></template>
                开启智能生成引擎
              </n-button>
           </div>
        </n-card>
        
        <!-- Quick Tips Bento -->
        <div class="studio-tips bento-card glass-panel">
           <div class="tips-header">
              <n-icon :component="Activity" :size="18" />
              <span>实验室提示</span>
           </div>
           <p>生成后的内容会自动匹配为您选择的 CSS 样式。您可以点击右侧的设备预览查看真实效果。</p>
        </div>
      </section>

      <!-- PREVIEW CANVAS -->
      <section class="preview-canvas">
         <div v-if="currentArticle" class="canvas-inner animate-reveal-in">
            <div class="device-mockup">
               <div class="m-bezel">
                  <div class="m-dynamic-island"></div>
                  <div class="m-screen">
                     <div class="m-status-bar">
                        <span>9:41</span>
                        <div class="m-icons">
                           <n-icon :component="Activity" :size="12" />
                        </div>
                     </div>
                     <div class="m-header">
                        <n-icon :component="ArrowLeft" :size="18" />
                        <span class="m-title">文章预览</span>
                        <n-icon :component="Menu" :size="18" />
                     </div>
                     <div class="m-scroll-content">
                        <div class="article-body" v-html="currentArticle.content_html"></div>
                     </div>
                     <div class="m-home-bar"></div>
                  </div>
               </div>
            </div>
            
            <div class="canvas-actions">
               <n-button circle tertiary @click="currentArticle = null">
                  <template #icon><n-icon :component="Trash2" /></template>
               </n-button>
            </div>
         </div>

         <div v-else class="canvas-empty animate-reveal-in">
            <div class="empty-illu">
               <n-icon :component="Monitor" :size="80" color="var(--border-color)" />
               <h3>就绪中...</h3>
               <p>请在左侧配置您的创作参数。生成后，实时渲染效果将展示在此处的移动端模型中。</p>
            </div>
         </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage, NCard, NInput, NButton, NIcon, NTag, NSpace } from 'naive-ui'
import { 
  Palette, Sparkles, Send, PenTool, Activity, 
  FileText, ChevronDown, LogOut, ArrowLeft, Zap, 
  Monitor, Trash2, Menu 
} from 'lucide-vue-next'
import { articleApi, type Style } from '@/api/article'
import { styleApi } from '@/api/style'

const router = useRouter()
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
    message.error('获取视觉样式失败')
  }
}

const fetchArticle = async (id: number) => {
  try {
    const article = await articleApi.getArticle(id)
    currentArticle.value = article
    theme.value = article.prompt_input || ''
  } catch (error) {
    message.error('获取文章失败')
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
    message.success('实验室内容生成成功')
  } catch (error: any) {
    message.error('生成引擎报错：' + (error.response?.data?.detail || '网络连接异常'))
  } finally {
    generating.value = false
  }
}

const handleSync = async () => {
  if (!currentArticle.value) return
  syncing.value = true
  try {
    await articleApi.syncArticle(currentArticle.value.id)
    message.success('已成功同步至微信草稿箱')
    currentArticle.value.synced_at = new Date().toISOString()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '同步指令未响应')
  } finally {
    syncing.value = false
  }
}

const handleBack = () => router.push({ name: 'Dashboard' })

onMounted(() => {
  fetchStyles()
  const id = route.query.id
  if (id) fetchArticle(Number(id))
})

watch(() => route.query.id, (newId) => {
  if (newId) fetchArticle(Number(newId))
  else {
    currentArticle.value = null
    theme.value = ''
  }
})
</script>

<style scoped>
.studio-root {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  height: 100%;
}

/* ========== STUDIO HEADER ========== */
.studio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.h-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.h-meta {
  display: flex;
  flex-direction: column;
}

.studio-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-main);
}

.studio-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
  font-weight: 600;
}

/* ========== STUDIO CONTENT LAYOUT ========== */
.studio-content {
  display: grid;
  grid-template-columns: 460px 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

/* Control Panel */
.control-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.control-inner {
  padding: var(--spacing-xl);
  border-radius: var(--radius-xl);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.f-label {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.studio-textarea :deep(.n-input-wrapper) {
  background: var(--bg-hover);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-tertiary);
}

/* Styles Studio Grid */
.studio-styles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}

.style-pill {
  height: 44px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-md);
  gap: var(--spacing-sm);
  cursor: pointer;
  border: 1px solid transparent;
  transition: all var(--transition-base);
  position: relative;
}

.style-pill:hover {
  background: white;
  border-color: var(--primary-hover);
  transform: translateX(4px);
}

.style-pill.active {
  background: white;
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px var(--primary-glow);
}

.pill-icon {
  color: var(--primary-color);
}

.pill-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.active-dot {
  position: absolute;
  right: 12px;
  width: 6px;
  height: 6px;
  background: var(--primary-color);
  border-radius: var(--radius-full);
}

.studio-btn-main {
  height: 52px !important;
  font-weight: 800 !important;
}

.studio-tips {
  padding: var(--spacing-md);
  background: var(--primary-soft);
  border: none;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  font-weight: 800;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.studio-tips p {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}

/* ========== PREVIEW CANVAS (DEVICE) ========== */
.preview-canvas {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: start;
}

.device-mockup {
  position: relative;
  width: 320px;
}

.m-bezel {
  width: 100%;
  height: 660px;
  background: #1e293b;
  border-radius: 44px;
  padding: 10px;
  box-shadow: 0 50px 100px -20px rgba(0,0,0,0.4);
}

.m-dynamic-island {
  position: absolute;
  top: 22px;
  left: 50%;
  transform: translateX(-50%);
  width: 90px;
  height: 24px;
  background: #000;
  border-radius: 12px;
  z-index: 10;
}

.m-screen {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 34px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.m-status-bar {
  height: 34px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  font-size: 11px;
  font-weight: 800;
}

.m-header {
  height: 44px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-md);
  justify-content: space-between;
}

.m-title {
  font-size: 14px;
  font-weight: 700;
}

.m-scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.m-scroll-content::-webkit-scrollbar { display: none; }

.article-body :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-sm);
}

.m-home-bar {
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.m-home-bar::after {
  content: '';
  width: 100px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
}

.canvas-actions {
  position: absolute;
  top: 0;
  right: -60px;
}

.canvas-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 500px;
}

.empty-illu {
  text-align: center;
  max-width: 320px;
}

.empty-illu h3 {
  margin-top: var(--spacing-md);
  font-size: 18px;
  font-weight: 800;
  color: var(--text-secondary);
}

.empty-illu p {
  font-size: 13px;
  color: var(--text-tertiary);
}
</style>
