import { ref, computed } from "vue";
import type { OfflineMode, OptimizeMode, RunPayload } from "../types";

export function useOfflineFlow() {
  const mode = ref<OfflineMode>("dynamic"); // 'dynamic' | 'steady'
  const optMode = ref<OptimizeMode>("manual"); // 'manual' | 'auto'
  const step = ref(1);

  const canNext = computed(() => {
    if (step.value === 1) return !!mode.value && !!optMode.value;
    return true;
  });

  function next() {
    step.value = Math.min(4, step.value + 1);
  }
  function prev() {
    step.value = Math.max(1, step.value - 1);
  }
  function reset() {
    step.value = 1;
  }

  const payload = ref<RunPayload>({
    mode: "dynamic",
    optMode: "manual",
    data: { source: "cleaned" },
    params: {},
    objectives: {},
    bounds: {},
  });

  return {
    mode,
    optMode,
    step,
    canNext,
    next,
    prev,
    reset,
    payload,
  };
}
