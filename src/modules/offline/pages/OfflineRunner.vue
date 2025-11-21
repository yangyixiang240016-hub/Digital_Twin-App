<template>
  <div class="offline-runner">
    <ol class="steps">
      <li :class="{ active: step === 1 }">1. Choose</li>
      <li :class="{ active: step === 2 }">2. SIM Data Settings</li>
      <li :class="{ active: step === 3 }">3. Set SIM Params</li>
      <li :class="{ active: step === 4 }">4. Generate SIM Results</li>
    </ol>

    <section v-if="step === 1">
      <div class="grid2">
        <div
          class="card"
          :class="{ active: mode === 'dynamic' }"
          @click="mode = 'dynamic'"
        >
          <h3>Dynamic</h3>
          <p>Replay historical conditions</p>
        </div>
        <div
          class="card"
          :class="{ active: mode === 'steady' }"
          @click="mode = 'steady'"
        >
          <h3>Steady-state</h3>
          <p>Sim equilibrium</p>
        </div>
        <div
          class="card"
          :class="{ active: optMode === 'manual' }"
          @click="optMode = 'manual'"
        >
          <h3>Manual</h3>
          <p>Set parameters</p>
        </div>
        <div
          class="card"
          :class="{ active: optMode === 'auto' }"
          @click="optMode = 'auto'"
        >
          <h3>Auto</h3>
          <p>Objectives & bounds</p>
        </div>
      </div>
      <div class="actions">
        <button class="btn" :disabled="!mode || !optMode" @click="next()">
          Next
        </button>
      </div>
    </section>

    <section v-else-if="step === 2">
      <DatasetPicker v-model="data" :type="mode" />
      <div class="actions">
        <button class="btn ghost" @click="prev()">Previous</button>
        <button class="btn" @click="next()">Next</button>
      </div>
    </section>

    <section v-else-if="step === 3">
      <ParamForm v-if="optMode === 'manual'" v-model="params" mode="manual" />
      <ParamForm v-else v-model="autoConf" mode="auto" />
      <div class="actions">
        <button class="btn ghost" @click="prev()">Previous</button>
        <button class="btn" @click="start()">Start {{ runLabel }}</button>
      </div>
    </section>

    <section v-else-if="step === 4">
      <RunStatus :loading="loading" :taskId="taskId" />
      <OfflineResult v-if="taskId && !loading" :taskId="taskId" />
      <div class="actions">
        <button class="btn" @click="reset()">Run again</button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import DatasetPicker from "../shared/DatasetPicker.vue";
import ParamForm from "../shared/ParamForm.vue";
import RunStatus from "../shared/RunStatus.vue";
import OfflineResult from "./OfflineResult.vue";
import {
  runOfflineDynamic,
  runOfflineSteady,
  runOfflineOptimize,
} from "@/api/offline";

const step = ref(1);
const mode = ref<"dynamic" | "steady">("dynamic");
const optMode = ref<"manual" | "auto">("manual");
const data = ref<any>({ source: "cleaned" });
const params = ref<any>({});
const autoConf = ref<any>({
  objectives: { TN: null, NH3N: null, NO3: null, TP: null, COD: null },
  weights: { TN: 1, NH3N: 1, NO3: 1, TP: 1, COD: 1 },
  bounds: {
    aerZone1: { min: 0, max: 99999 },
    aerZone2: { min: 0, max: 99999 },
    aerZone3: { min: 0, max: 99999 },
    aerZone4: { min: 0, max: 99999 },
    MLR: { min: 0, max: 99999 },
    RAS: { min: 0, max: 99999 },
    SAS: { min: 0, max: 99999 },
    PAC: { min: 0, max: 99999 },
  },
});
const loading = ref(false);
const taskId = ref<string | null>(null);

function next() {
  step.value = Math.min(4, step.value + 1);
}
function prev() {
  step.value = Math.max(1, step.value - 1);
}
function reset() {
  step.value = 1;
  taskId.value = null;
  loading.value = false;
}

const runLabel = computed(() =>
  optMode.value === "auto"
    ? "Optimization"
    : mode.value === "steady"
    ? "Steady SIM"
    : "Dynamic SIM"
);

async function start() {
  loading.value = true;
  step.value = 4;
  try {
    if (optMode.value === "auto") {
      const r = await runOfflineOptimize({
        mode: mode.value,
        data: data.value,
        config: autoConf.value,
      });
      taskId.value = r?.taskId || null;
    } else if (mode.value === "steady") {
      const r = await runOfflineSteady({
        data: data.value,
        params: params.value,
      });
      taskId.value = r?.taskId || null;
    } else {
      const r = await runOfflineDynamic({
        data: data.value,
        params: params.value,
      });
      taskId.value = r?.taskId || null;
    }
  } catch (e: any) {
    alert(e?.message || "Start failed");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.offline-runner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
  display: grid;
  gap: 16px;
}
.steps {
  display: flex;
  gap: 8px;
  list-style: none;
  padding: 0;
  margin: 12px 0 20px;
}
.steps li {
  padding: 6px 10px;
  border-radius: 8px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
}
.steps li.active {
  background: #e0ecff;
  border-color: #93c5fd;
}
.grid2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
}
.card.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #2563eb;
  color: white;
  cursor: pointer;
}
.btn.ghost {
  background: white;
  color: #111827;
}
</style>
