<template>
  <div class="form">
    <template v-if="mode !== 'auto'">
      <div v-for="f in manualFields" :key="f" class="row">
        <label>{{ labels[f] || f }}</label>
        <input type="number" step="0.01" v-model.number="model[f]" />
      </div>
    </template>
    <template v-else>
      <fieldset class="box">
        <legend>Objectives</legend>
        <div class="row" v-for="k in objectives" :key="k">
          <label>{{ k }} target</label>
          <input
            type="number"
            step="0.01"
            v-model.number="model.objectives[k]"
          />
          <label>Weight</label>
          <input type="number" step="0.01" v-model.number="model.weights[k]" />
        </div>
      </fieldset>
      <fieldset class="box">
        <legend>Variable bounds</legend>
        <div class="row" v-for="k in bounds" :key="k">
          <label>{{ labels[k] || k }} min</label>
          <input
            type="number"
            step="0.01"
            v-model.number="model.bounds[k].min"
          />
          <label>max</label>
          <input
            type="number"
            step="0.01"
            v-model.number="model.bounds[k].max"
          />
        </div>
      </fieldset>
    </template>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from "vue";
const props = defineProps<{ modelValue: any; mode?: "auto" | "manual" }>();
const emit = defineEmits(["update:modelValue"]);
const model = reactive<any>(JSON.parse(JSON.stringify(props.modelValue || {})));
watch(model, () => emit("update:modelValue", model), { deep: true });

const manualFields = [
  "aerZone1",
  "aerZone2",
  "aerZone3",
  "aerZone4",
  "MLR",
  "RAS",
  "SAS",
  "PAC",
];
const objectives = ["TN", "NH3N", "NO3", "TP", "COD"];
const bounds = manualFields;

const labels: Record<string, string> = {
  aerZone1: "Aeration Zone 1 (Nm³/d)",
  aerZone2: "Aeration Zone 2 (Nm³/d)",
  aerZone3: "Aeration Zone 3 (Nm³/d)",
  aerZone4: "Aeration Zone 4 (Nm³/d)",
  MLR: "MLR Return Flow (m³/d)",
  RAS: "RAS Return Flow (m³/d)",
  SAS: "SAS Sludge Rate (m³/d)",
  PAC: "PAC dosage (mg/L)",
};
</script>

<style scoped>
.form {
  display: grid;
  gap: 12px;
}
.row {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 12px;
  align-items: center;
}
.box {
  border: 1px solid #e5e7eb;
  padding: 12px;
  border-radius: 12px;
}
legend {
  font-weight: 600;
}
</style>
