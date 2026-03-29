<script setup>
import { reactive, ref, computed, watch } from 'vue'

const props = defineProps({
  schema: { type: Object, required: true },
  targetFormat: { type: String, default: '' },
})

const emit = defineEmits(['update:settings'])

const values = reactive({})
const showAdvanced = ref(false)

const basicSettings = computed(() => {
  const entries = {}
  for (const [key, def] of Object.entries(props.schema)) {
    if (def.advanced) continue
    if (def.formats && !def.formats.includes(props.targetFormat)) continue
    entries[key] = def
  }
  return entries
})

const advancedSettings = computed(() => {
  const entries = {}
  for (const [key, def] of Object.entries(props.schema)) {
    if (!def.advanced) continue
    if (def.formats && !def.formats.includes(props.targetFormat)) continue
    entries[key] = def
  }
  return entries
})

const hasAdvanced = computed(() => Object.keys(advancedSettings.value).length > 0)

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

watch(
  () => props.targetFormat,
  () => {
    showAdvanced.value = false
  }
)

function onInput(key, value) {
  values[key] = value
  emit('update:settings', { ...values })
}
</script>

<template>
  <div v-if="Object.keys(schema).length" class="settings-panel">
    <div class="settings-row">
      <template v-for="(def, key) in basicSettings" :key="key">
        <div class="setting" v-if="!def.optional || values[key] !== undefined">
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

          <template v-else-if="def.type === 'checkbox'">
            <input
              type="checkbox"
              :checked="values[key] ?? def.default"
              class="checkbox-input"
              @change="onInput(key, $event.target.checked)"
            />
          </template>
        </div>
      </template>
    </div>

    <div v-if="hasAdvanced" class="advanced-section">
      <label class="advanced-toggle">
        <input
          type="checkbox"
          :checked="showAdvanced"
          @change="showAdvanced = $event.target.checked"
        />
        <span>Advanced</span>
      </label>

      <div v-if="showAdvanced" class="settings-row advanced-row">
        <template v-for="(def, key) in advancedSettings" :key="key">
          <div class="setting">
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

            <template v-else-if="def.type === 'checkbox'">
              <input
                type="checkbox"
                :checked="values[key] ?? def.default"
                class="checkbox-input"
                @change="onInput(key, $event.target.checked)"
              />
            </template>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.settings-row {
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

.checkbox-input {
  accent-color: var(--accent);
  width: 16px;
  height: 16px;
}

.advanced-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.advanced-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  user-select: none;
}

.advanced-toggle input {
  accent-color: var(--accent);
}

.advanced-row {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
</style>
