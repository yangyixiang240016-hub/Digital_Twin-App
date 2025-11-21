<template>
  <div class="picker">
    <div class="row">
      <label>Data source</label>
      <select v-model="model.source">
        <option value="raw">Raw</option>
        <option value="cleaned">Cleaned</option>
        <option value="lab">Lab</option>
      </select>
    </div>

    <div v-if="type === 'dynamic'">
      <div class="row">
        <label>Start date</label>
        <input type="datetime-local" v-model="model.start" />
      </div>
      <div class="row">
        <label>End date</label>
        <input type="datetime-local" v-model="model.end" />
      </div>
    </div>

    <div v-else class="grid3">
      <div v-for="k in influentKeys" :key="k" class="row">
        <label>{{ k }}</label>
        <input type="number" step="0.01" v-model.number="model.influent[k]" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";
const props = defineProps<{ modelValue: any; type: "dynamic" | "steady" }>();
const emit = defineEmits(["update:modelValue"]);
const model = reactive<any>({
  ...props.modelValue,
  influent: props.modelValue?.influent || {},
});
const influentKeys = ["flow", "COD", "TN", "NH3N", "TP", "NO3", "pH", "SS"];
watch(model, () => emit("update:modelValue", model), { deep: true });
</script>

<style scoped>
.picker {
  display: grid;
  gap: 12px;
}
.row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 12px;
  align-items: center;
}
.grid3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
</style>
