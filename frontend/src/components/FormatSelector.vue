<script setup>
const props = defineProps({
  targets: { type: Array, required: true },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="format-selector">
    <label class="label">Convert to:</label>
    <select
      class="format-select"
      :value="modelValue"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>Select format...</option>
      <option v-for="fmt in targets" :key="fmt" :value="fmt">
        {{ fmt.toUpperCase() }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.format-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.format-select {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
}
</style>
