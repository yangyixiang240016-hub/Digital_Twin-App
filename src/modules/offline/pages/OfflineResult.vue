<template>
  <div class="offline-result">
    <RunStatus :loading="loading" :taskId="taskId" />
    <ResultCharts
      v-if="!loading && result"
      :baseline="result.baseline"
      :result="result.effluent"
      :before="result.before"
      :after="result.after"
    />
    <ResultTable v-if="!loading && result" :rows="result.rows" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import RunStatus from "../shared/RunStatus.vue";
import ResultCharts from "../shared/ResultCharts.vue";
import ResultTable from "../shared/ResultTable.vue";
import { fetchOfflineResult } from "@/api/offline";

const props = defineProps<{ taskId: string | null }>();
const loading = ref(true);
const result = ref<any>(null);
const taskId = ref(props.taskId);

async function poll() {
  if (!taskId.value) return;
  let tries = 0;
  while (tries++ < 60) {
    const r = await fetchOfflineResult(taskId.value);
    if (r?.status === "done") {
      result.value = r.payload;
      loading.value = false;
      return;
    }
    await new Promise((res) => setTimeout(res, 1000));
  }
  loading.value = false;
}

onMounted(poll);
watch(
  () => props.taskId,
  (n) => {
    taskId.value = n;
    loading.value = true;
    result.value = null;
    poll();
  }
);
</script>

<style scoped>
.offline-result {
  display: grid;
  gap: 16px;
}
</style>
