// # 离线流程 Pinia 状态（选择项、步骤、运行状态）
import { defineStore } from "pinia";
import type {
  OfflineSelection,
  StepKey,
  TaskInfo,
  ResultData,
} from "@/modules/offline/types";

export const useOfflineStore = defineStore("offline", {
  state: () => ({
    selection: null as OfflineSelection | null,
    currentStep: "dataset" as StepKey,
    task: null as TaskInfo | null,
    result: null as ResultData | null,
  }),
  actions: {
    setSelection(sel: OfflineSelection) {
      this.selection = sel;
      this.currentStep = "dataset";
    },
    setStep(step: StepKey) {
      this.currentStep = step;
    },
    setTask(task: TaskInfo | null) {
      this.task = task;
    },
    setResult(res: ResultData | null) {
      this.result = res;
    },
    reset() {
      this.currentStep = "dataset";
      this.task = null;
      this.result = null;
    },
  },
});
