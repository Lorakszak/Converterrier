<script setup>
defineProps({
  disabled: { type: Boolean, default: false },
  converting: { type: Boolean, default: false },
})

const emit = defineEmits(['convert'])
</script>

<template>
  <button
    class="convert-btn"
    :class="{ converting }"
    :disabled="disabled || converting"
    @click="emit('convert')"
  >
    <template v-if="converting">
      <span class="spinner"></span> Converting...
    </template>
    <template v-else>
      Convert & Download
    </template>
  </button>
</template>

<style scoped>
.convert-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  color: white;
  padding: 12px 48px;
  border-radius: var(--radius);
  font-weight: 600;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.convert-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.convert-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
