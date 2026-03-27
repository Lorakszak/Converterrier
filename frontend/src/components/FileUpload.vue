<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])
const dragging = ref(false)
const fileInput = ref(null)

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) emit('file-selected', file)
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) emit('file-selected', file)
}

function openFilePicker() {
  fileInput.value.click()
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragging }"
    @dragover.prevent="dragging = true"
    @dragleave="dragging = false"
    @drop.prevent="onDrop"
    @click="openFilePicker"
  >
    <input
      ref="fileInput"
      type="file"
      hidden
      @change="onFileChange"
    />
    <div class="dropzone-icon">📁</div>
    <p class="dropzone-text">Drag & drop a file here</p>
    <p class="dropzone-hint">or <span class="link">browse files</span></p>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed rgba(74, 111, 165, 0.6);
  border-radius: var(--radius);
  padding: 48px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.dropzone:hover,
.dropzone.dragging {
  border-color: var(--accent);
  background: rgba(59, 130, 246, 0.05);
}

.dropzone-icon { font-size: 2.5rem; margin-bottom: 8px; }
.dropzone-text { font-size: 1rem; margin-bottom: 4px; }
.dropzone-hint { color: var(--text-muted); font-size: 0.85rem; }
.link { color: var(--accent); text-decoration: underline; }
</style>
