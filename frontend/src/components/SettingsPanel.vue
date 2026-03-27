<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  schema: { type: Object, required: true },
})

const emit = defineEmits(['update:settings'])

const values = reactive({})

watch(
  () => props.schema,
  (schema) => {
    Object.keys(values).forEach((k) => delete values[k])
    for (const [key, def] of Object.entries(schema)) {
      if (def.default !== undefined) {
        values[key] = def.default
      }
    }
    emit('update:settings', { ...values })
  },
  { immediate: true }
)

function onInput(key, value) {
  values[key] = value
  emit('update:settings', { ...values })
}
</script>

<template>
  <div v-if="Object.keys(schema).length" class="settings-panel">
    <div v-for="(def, key) in schema" :key="key" class="setting">
      <template v-if="!def.optional || values[key] !== undefined">
        <label class="setting-label">{{ def.label }}:</label>

        <template v-if="def.type === 'range'">
          <input
            type="range"
            :min="def.min"
            :max="def.max"
            :value="values[key] ?? def.default"
            class="range-input"
            @input="onInput(key, Number($event.target.value))"
          />
          <span class="range-value">{{ values[key] ?? def.default }}</span>
        </template>

        <template v-else-if="def.type === 'select'">
          <select
            class="select-input"
            :value="values[key] ?? def.default"
            @change="onInput(key, $event.target.value)"
          >
            <option v-for="opt in def.options" :key="opt" :value="opt">
              {{ opt }}
            </option>
          </select>
        </template>

        <template v-else-if="def.type === 'number'">
          <input
            type="number"
            :value="values[key]"
            :placeholder="def.label"
            class="number-input"
            @input="onInput(key, $event.target.value ? Number($event.target.value) : undefined)"
          />
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.setting {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
  white-space: nowrap;
}

.range-input {
  width: 100px;
  accent-color: var(--accent);
}

.range-value {
  color: var(--text-primary);
  font-size: 0.8rem;
  min-width: 2em;
}

.select-input {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.number-input {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  width: 80px;
}
</style>
