<script setup>
import { ref, computed, onMounted } from 'vue'
import FileUpload from './components/FileUpload.vue'
import FormatSelector from './components/FormatSelector.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import ConvertButton from './components/ConvertButton.vue'
import BatchMode from './components/BatchMode.vue'

const health = ref({ ffmpeg: false, pandoc: false, pandoc_pdf: false })
const formats = ref({})
const error = ref('')
const selectedFile = ref(null)
const selectedFiles = ref([])
const targetFormat = ref('')
const settings = ref({})
const converting = ref(false)
const batchMode = ref(false)

const fileInfo = computed(() => {
  if (!selectedFile.value) return null
  const name = selectedFile.value.name
  const ext = name.split('.').pop().toLowerCase()
  const size = selectedFile.value.size
  let category = null
  for (const [cat, catFormats] of Object.entries(formats.value)) {
    if (ext in catFormats) {
      category = cat
      break
    }
  }
  return { name, ext, size, category }
})

const availableTargets = computed(() => {
  if (!fileInfo.value?.category || !fileInfo.value?.ext) return []
  const cat = formats.value[fileInfo.value.category]
  if (!cat || !cat[fileInfo.value.ext]) return []
  return cat[fileInfo.value.ext].targets
})

const settingsSchema = computed(() => {
  if (!fileInfo.value?.category || !fileInfo.value?.ext) return {}
  const cat = formats.value[fileInfo.value.category]
  if (!cat || !cat[fileInfo.value.ext]) return {}
  return cat[fileInfo.value.ext].settings
})

const batchInfo = computed(() => {
  if (!selectedFiles.value.length) return null
  const first = selectedFiles.value[0]
  const ext = first.name.split('.').pop().toLowerCase()
  let category = null
  for (const [cat, catFormats] of Object.entries(formats.value)) {
    if (ext in catFormats) {
      category = cat
      break
    }
  }
  return { ext, category, count: selectedFiles.value.length }
})

const batchTargets = computed(() => {
  if (!batchInfo.value?.category || !batchInfo.value?.ext) return []
  const cat = formats.value[batchInfo.value.category]
  if (!cat || !cat[batchInfo.value.ext]) return []
  return cat[batchInfo.value.ext].targets
})

const batchSettingsSchema = computed(() => {
  if (!batchInfo.value?.category || !batchInfo.value?.ext) return {}
  const cat = formats.value[batchInfo.value.category]
  if (!cat || !cat[batchInfo.value.ext]) return {}
  return cat[batchInfo.value.ext].settings
})

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function onFileSelected(file) {
  selectedFile.value = file
  targetFormat.value = ''
  settings.value = {}
  error.value = ''
}

function removeFile() {
  selectedFile.value = null
  targetFormat.value = ''
  settings.value = {}
}

function onBatchFilesSelected(files) {
  selectedFiles.value = files
  targetFormat.value = ''
  settings.value = {}
  error.value = ''
}

function clearBatch() {
  selectedFiles.value = []
  targetFormat.value = ''
  settings.value = {}
}

async function doConvert() {
  if (!selectedFile.value || !targetFormat.value) return

  converting.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('target_format', targetFormat.value)
    formData.append('settings', JSON.stringify(settings.value))

    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Conversion failed')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedFile.value.name.replace(/\.[^.]+$/, '')}.${targetFormat.value}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  } finally {
    converting.value = false
  }
}

async function doBatchConvert() {
  if (!selectedFiles.value.length || !targetFormat.value) return

  converting.value = true
  error.value = ''

  try {
    const formData = new FormData()
    for (const file of selectedFiles.value) {
      formData.append('files', file)
    }
    formData.append('target_format', targetFormat.value)
    formData.append('settings', JSON.stringify(settings.value))

    const response = await fetch('/api/convert/batch', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Batch conversion failed')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'converted.zip'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  } finally {
    converting.value = false
  }
}

onMounted(async () => {
  try {
    const [healthRes, formatsRes] = await Promise.all([
      fetch('/api/health'),
      fetch('/api/formats'),
    ])
    health.value = await healthRes.json()
    formats.value = await formatsRes.json()
  } catch (e) {
    error.value = 'Failed to connect to backend'
  }
})
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <span class="logo">🐕</span>
        <span class="app-name">Converterrier</span>
      </div>
      <div class="header-right">
        <span :class="['status', health.ffmpeg ? 'ok' : 'missing']">
          {{ health.ffmpeg ? '●' : '○' }} FFmpeg
        </span>
        <span :class="['status', health.pandoc ? 'ok' : 'missing']">
          {{ health.pandoc ? '●' : '○' }} Pandoc
        </span>
      </div>
    </header>

    <main class="main">
      <div class="tabs">
        <button :class="['tab', { active: !batchMode }]" @click="batchMode = false">
          Single File
        </button>
        <button :class="['tab', { active: batchMode }]" @click="batchMode = true">
          Batch Mode
        </button>
      </div>

      <div class="content-area">
        <p v-if="error" class="error-banner">{{ error }}</p>

        <!-- Single file mode -->
        <template v-if="!batchMode">
          <FileUpload v-if="!selectedFile" @file-selected="onFileSelected" />

          <div v-else class="file-info">
            <div class="file-info-row">
              <div class="file-details">
                <span class="format-badge">{{ fileInfo.ext.toUpperCase() }}</span>
                <span class="file-name">{{ fileInfo.name }}</span>
                <span class="file-size">{{ formatFileSize(fileInfo.size) }}</span>
              </div>
              <button class="remove-btn" @click="removeFile">✕ Remove</button>
            </div>
            <p v-if="!fileInfo.category" class="warning">
              Unsupported file format
            </p>
          </div>

          <div v-if="selectedFile && fileInfo?.category" class="conversion-row">
            <FormatSelector
              v-model="targetFormat"
              :targets="availableTargets"
            />
            <div v-if="targetFormat" class="settings-divider"></div>
            <SettingsPanel
              v-if="targetFormat"
              :schema="settingsSchema"
              @update:settings="settings = $event"
            />
          </div>

          <div v-if="selectedFile && targetFormat" class="convert-area">
            <ConvertButton
              :disabled="!targetFormat"
              :converting="converting"
              @convert="doConvert"
            />
          </div>
        </template>

        <!-- Batch mode -->
        <template v-if="batchMode">
          <BatchMode v-if="!selectedFiles.length" @files-selected="onBatchFilesSelected" />

          <template v-else>
            <div class="file-info">
              <div class="file-info-row">
                <div class="file-details">
                  <span class="format-badge">{{ batchInfo?.ext?.toUpperCase() }}</span>
                  <span class="file-name">{{ batchInfo?.count }} files selected</span>
                </div>
                <button class="remove-btn" @click="clearBatch">✕ Clear</button>
              </div>
              <ul class="batch-list">
                <li v-for="(f, i) in selectedFiles" :key="i" class="batch-item">
                  {{ f.name }} — {{ formatFileSize(f.size) }}
                </li>
              </ul>
            </div>

            <div v-if="batchInfo?.category" class="conversion-row">
              <FormatSelector v-model="targetFormat" :targets="batchTargets" />
              <div v-if="targetFormat" class="settings-divider"></div>
              <SettingsPanel
                v-if="targetFormat"
                :schema="batchSettingsSchema"
                @update:settings="settings = $event"
              />
            </div>

            <div v-if="targetFormat" class="convert-area">
              <ConvertButton
                :disabled="!targetFormat"
                :converting="converting"
                @convert="doBatchConvert"
              />
            </div>
          </template>
        </template>
      </div>
    </main>

    <footer class="footer">
      All conversions happen locally on your machine — no files are uploaded anywhere
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 16px 24px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}

.header-left { display: flex; align-items: center; gap: 10px; }
.logo { font-size: 1.4rem; }
.app-name { font-size: 1.1rem; font-weight: 600; }
.header-right { display: flex; gap: 16px; font-size: 0.85rem; }
.status.ok { color: var(--success); }
.status.missing { color: var(--error); }

.main {
  flex: 1;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 0;
}

.tab {
  padding: 8px 16px;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius) var(--radius) 0 0;
  font-size: 0.85rem;
  font-weight: 500;
}

.tab.active {
  background: var(--bg-card);
  color: var(--text-primary);
}

.content-area {
  background: var(--bg-card);
  padding: 24px;
  border-radius: 0 var(--radius) var(--radius) var(--radius);
}

.error-banner {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid var(--error);
  color: var(--error);
  padding: 12px 16px;
  border-radius: var(--radius);
}

.file-info {
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.file-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.file-details { display: flex; align-items: center; gap: 10px; }

.format-badge {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.file-name { font-size: 0.9rem; }
.file-size { color: var(--text-muted); font-size: 0.8rem; }

.remove-btn {
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
}

.remove-btn:hover { color: var(--error); }

.warning {
  color: var(--warning);
  font-size: 0.85rem;
  margin-top: 12px;
}

.conversion-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.settings-divider {
  width: 1px;
  height: 24px;
  background: var(--border);
}

.convert-area {
  margin-top: 20px;
  text-align: center;
}

.batch-list {
  list-style: none;
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.batch-item {
  padding: 4px 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}

.batch-item:last-child {
  border-bottom: none;
}

.footer {
  padding: 12px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
