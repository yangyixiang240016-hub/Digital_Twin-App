import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import type { BackendSystemParams } from "@/api/systemParams";

export interface SimulationParams {
  basicSettings: {
    dataType: string;
    inletTimePrediction: string;
    simulationTimeInterval: string;
    autoCalibrationPeriod: string;
  };
  deviationSettings: {
    codRelativeError: { enabled: boolean; value: number };
    nh3nAbsoluteError: { enabled: boolean; value: number };
    ssRelativeError: { enabled: boolean; value: number };
    tpAbsoluteError: { enabled: boolean; value: number };
    tnRelativeError: { enabled: boolean; value: number };
    do1_1PercentageError: { enabled: boolean; value: number };
    do1_2PercentageError: { enabled: boolean; value: number };
    do2_1PercentageError: { enabled: boolean; value: number };
    do2_2PercentageError: { enabled: boolean; value: number };
  };
  cleaningAlgorithm: string;
  cleaningObjects: Record<
    | "inletNH3N"
    | "inletTN"
    | "inletTP"
    | "inletCOD"
    | "inletSS"
    | "AAODO"
    | "MBRDO",
    boolean
  >;
  effluentConstraints: {
    cod: number;
    nh3n: number;
    ss: number;
    tp: number;
    tn: number;
  };
  hyperparameters: {
    iterations: number;
    populationSize: number;
    simulationStepSize: number;
    mutationThreshold: number;
    chaosFactor: number;
  };
}

type CleaningObjectKey = keyof SimulationParams["cleaningObjects"];

const BACKEND_FIELD_DEFAULTS: BackendSystemParams = {
  predict_algorithm_sp: 0,
  predict_steps_sp: 12,
  simulate_interval_sp: 120,
  data_type_sp: 0,
  calibration_period_sp: 30,
  optimize_algorithm_sp: "",
  cleaning_algorithm_sp: 0,
  tolerance_cod_sp: 0,
  tolerance_snhx_sp: 0,
  tolerance_xtss_sp: 0,
  tolerance_tp_sp: 0,
  tolerance_tn_sp: 0,
  tolerance_do_1_1_sp: 0,
  tolerance_do_1_2_sp: 0,
  tolerance_do_2_1_sp: 0,
  tolerance_do_2_2_sp: 0,
  hyper_p_iterations_sp: 0,
  hyper_p_threshold_sp: 0,
  hyper_p_size_sp: 0,
  hyper_p_chaosfactor_sp: 0,
  hyper_p_stepsize_sp: 0,
  cleaning_objects_sp: [],
  limit_cod_sp: 0,
  limit_nh3_n_sp: 0,
  limit_tp_sp: 0,
  limit_tn_sp: 0,
  limit_ss_sp: 0,
};

const PREDICT_STEP_OPTIONS = ["12小时", "24小时", "48小时"];

// 前端显示值到后端值的映射（前端显示 -> 后端值）
const FRONT_TO_BACK_PREDICT_HOURS: Record<string, number> = {
  "12小时": 6,
  "24小时": 12,
  "48小时": 24,
};

// 后端值到前端显示值的映射（后端值 -> 前端显示）
const BACK_TO_FRONT_PREDICT_HOURS: Record<number, string> = {
  6: "12小时",
  12: "24小时",
  24: "48小时",
};
const SIM_INTERVAL_OPTIONS = ["1小时", "2小时", "4小时", "24小时"];
const DATA_TYPE_LABELS = ["原始数据", "清洗数据", "化验室数据"];
const CLEANING_ALGO_LABELS: Record<number, string> = {
  0: "原始数据",
  1: "清洗算法一",
  2: "清洗算法二",
};
const CLEANING_ALGO_REVERSE: Record<string, number> = {
  原始数据: 0,
  清洗算法一: 1,
  清洗算法二: 2,
};

const CLEANING_OBJECT_FRONT_TO_BACK: Record<CleaningObjectKey, string> = {
  inletNH3N: "NH3-N",
  inletTN: "TN",
  inletTP: "TP",
  inletCOD: "COD",
  inletSS: "SS",
  AAODO: "AAODO",
  MBRDO: "MBRDO",
};

const DEVIATION_MAPPING: Array<{
  front: keyof SimulationParams["deviationSettings"];
  backend:
    | "tolerance_cod_sp"
    | "tolerance_snhx_sp"
    | "tolerance_xtss_sp"
    | "tolerance_tp_sp"
    | "tolerance_tn_sp"
    | "tolerance_do_1_1_sp"
    | "tolerance_do_1_2_sp"
    | "tolerance_do_2_1_sp"
    | "tolerance_do_2_2_sp";
}> = [
  { front: "codRelativeError", backend: "tolerance_cod_sp" },
  { front: "nh3nAbsoluteError", backend: "tolerance_snhx_sp" },
  { front: "ssRelativeError", backend: "tolerance_xtss_sp" },
  { front: "tpAbsoluteError", backend: "tolerance_tp_sp" },
  { front: "tnRelativeError", backend: "tolerance_tn_sp" },
  { front: "do1_1PercentageError", backend: "tolerance_do_1_1_sp" },
  { front: "do1_2PercentageError", backend: "tolerance_do_1_2_sp" },
  { front: "do2_1PercentageError", backend: "tolerance_do_2_1_sp" },
  { front: "do2_2PercentageError", backend: "tolerance_do_2_2_sp" },
];

const DEFAULT_DEVIATION_VALUES: Record<
  keyof SimulationParams["deviationSettings"],
  number
> = {
  codRelativeError: 30,
  nh3nAbsoluteError: 0.3,
  ssRelativeError: 30,
  tpAbsoluteError: 0.3,
  tnRelativeError: 30,
  do1_1PercentageError: 50,
  do1_2PercentageError: 50,
  do2_1PercentageError: 50,
  do2_2PercentageError: 50,
};

const defaultParams: SimulationParams = {
  basicSettings: {
    dataType: "清洗数据",
    inletTimePrediction: "12小时",
    simulationTimeInterval: "2小时",
    autoCalibrationPeriod: "30天",
  },
  deviationSettings: {
    codRelativeError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.codRelativeError,
    },
    nh3nAbsoluteError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.nh3nAbsoluteError,
    },
    ssRelativeError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.ssRelativeError,
    },
    tpAbsoluteError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.tpAbsoluteError,
    },
    tnRelativeError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.tnRelativeError,
    },
    do1_1PercentageError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.do1_1PercentageError,
    },
    do1_2PercentageError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.do1_2PercentageError,
    },
    do2_1PercentageError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.do2_1PercentageError,
    },
    do2_2PercentageError: {
      enabled: true,
      value: DEFAULT_DEVIATION_VALUES.do2_2PercentageError,
    },
  },
  cleaningAlgorithm: "原始数据",
  cleaningObjects: {
    inletNH3N: true,
    inletTN: true,
    inletTP: true,
    inletCOD: true,
    inletSS: true,
    AAODO: true,
    MBRDO: true,
  },
  effluentConstraints: {
    cod: 30,
    nh3n: 2,
    ss: 8,
    tp: 0.4,
    tn: 15,
  },
  hyperparameters: {
    iterations: 10,
    populationSize: 10,
    simulationStepSize: 1,
    mutationThreshold: 0.001,
    chaosFactor: 0.499,
  },
};

export const useSimulationParamsStore = defineStore("simulationParams", () => {
  const params = reactive<SimulationParams>(
    JSON.parse(JSON.stringify(defaultParams))
  );
  const backendSnapshot = ref<BackendSystemParams | null>(null);
  const predictAlgorithm = ref<"arima" | "transformer">("arima");

  function getParams(): SimulationParams {
    return params;
  }

  function updateParams(newParams: Partial<SimulationParams>): void {
    Object.assign(params, newParams);
    saveToLocalStorage();
  }

  function resetParams(): void {
    Object.assign(params, JSON.parse(JSON.stringify(defaultParams)));
    saveToLocalStorage();
  }

  function saveToLocalStorage(): void {
    try {
      localStorage.setItem("simulationParams", JSON.stringify(params));
    } catch (error) {
      console.warn("保存参数到本地存储失败:", error);
    }
  }

  function loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem("simulationParams");
      if (stored) {
        const parsed = JSON.parse(stored);
        Object.assign(params, parsed);
      }
    } catch (error) {
      console.warn("从本地存储加载参数失败:", error);
    }
  }

  function applyBackendParams(data: BackendSystemParams): void {
    const sanitized: BackendSystemParams = { ...BACKEND_FIELD_DEFAULTS };
    Object.entries(BACKEND_FIELD_DEFAULTS).forEach(([key, defaultVal]) => {
      const incoming = (data as any)?.[key];
      if (incoming !== undefined) {
        if (incoming === "" && typeof defaultVal !== "string") {
          (sanitized as any)[key] = defaultVal;
        } else {
          (sanitized as any)[key] = incoming;
        }
      } else {
        (sanitized as any)[key] = defaultVal;
      }
    });
    sanitized.cleaning_objects_sp = Array.isArray(data?.cleaning_objects_sp)
      ? data!.cleaning_objects_sp
      : [];
    backendSnapshot.value = sanitized;
    const snapshot = backendSnapshot.value;

    predictAlgorithm.value =
      snapshot.predict_algorithm_sp === 1 ? "transformer" : "arima";

    const resolvedDataType =
      DATA_TYPE_LABELS[snapshot.data_type_sp] || DATA_TYPE_LABELS[0];
    params.basicSettings.dataType = resolvedDataType;

    const predictHours =
      snapshot.predict_steps_sp ?? BACKEND_FIELD_DEFAULTS.predict_steps_sp;
    // 将后端值映射到前端显示值
    params.basicSettings.inletTimePrediction =
      BACK_TO_FRONT_PREDICT_HOURS[predictHours] || "12小时";

    const simMinutes =
      snapshot.simulate_interval_sp ??
      BACKEND_FIELD_DEFAULTS.simulate_interval_sp;
    params.basicSettings.simulationTimeInterval =
      simMinutes % 60 === 0 ? `${simMinutes / 60}小时` : `${simMinutes}分钟`;
    params.basicSettings.autoCalibrationPeriod = `${snapshot.calibration_period_sp}天`;

    const resolvedCleaningAlgo =
      CLEANING_ALGO_LABELS[snapshot.cleaning_algorithm_sp] ||
      CLEANING_ALGO_LABELS[0];
    params.cleaningAlgorithm = resolvedCleaningAlgo;
    backendSnapshot.value.cleaning_algorithm_sp =
      CLEANING_ALGO_REVERSE[resolvedCleaningAlgo] ?? 0;

    const selected = new Set(snapshot.cleaning_objects_sp || []);
    (Object.keys(CLEANING_OBJECT_FRONT_TO_BACK) as CleaningObjectKey[]).forEach(
      (frontKey) => {
        params.cleaningObjects[frontKey] = selected.has(
          CLEANING_OBJECT_FRONT_TO_BACK[frontKey]
        );
      }
    );

    DEVIATION_MAPPING.forEach(({ front, backend }) => {
      const value = snapshot[backend] ?? 0;
      params.deviationSettings[front].enabled = value > 0;
      params.deviationSettings[front].value =
        value > 0
          ? Number(value)
          : params.deviationSettings[front].value ||
            DEFAULT_DEVIATION_VALUES[front];
    });

    params.hyperparameters.iterations = Number(
      snapshot.hyper_p_iterations_sp ?? params.hyperparameters.iterations
    );
    params.hyperparameters.populationSize = Number(
      snapshot.hyper_p_size_sp ?? params.hyperparameters.populationSize
    );
    params.hyperparameters.simulationStepSize = Number(
      snapshot.hyper_p_stepsize_sp ?? params.hyperparameters.simulationStepSize
    );
    params.hyperparameters.mutationThreshold = Number(
      snapshot.hyper_p_threshold_sp ?? params.hyperparameters.mutationThreshold
    );
    params.hyperparameters.chaosFactor = Number(
      snapshot.hyper_p_chaosfactor_sp ?? params.hyperparameters.chaosFactor
    );

    params.effluentConstraints.cod = Number(
      snapshot.limit_cod_sp ?? params.effluentConstraints.cod
    );
    params.effluentConstraints.nh3n = Number(
      snapshot.limit_nh3_n_sp ?? params.effluentConstraints.nh3n
    );
    params.effluentConstraints.tp = Number(
      snapshot.limit_tp_sp ?? params.effluentConstraints.tp
    );
    params.effluentConstraints.tn = Number(
      snapshot.limit_tn_sp ?? params.effluentConstraints.tn
    );
    params.effluentConstraints.ss = Number(
      snapshot.limit_ss_sp ?? params.effluentConstraints.ss
    );

    saveToLocalStorage();
  }

  function buildBackendPayload(
    currentParams: SimulationParams,
    options: { predictAlgorithm: "arima" | "transformer" }
  ): BackendSystemParams {
    const base = {
      ...BACKEND_FIELD_DEFAULTS,
      ...(backendSnapshot.value || {}),
    };

    const payload: BackendSystemParams = {
      ...base,
      predict_algorithm_sp: options.predictAlgorithm === "transformer" ? 1 : 0,
      predict_steps_sp: extractPredictHours(
        currentParams.basicSettings.inletTimePrediction
      ),
      simulate_interval_sp: extractSimIntervalMinutes(
        currentParams.basicSettings.simulationTimeInterval
      ),
      data_type_sp: Math.max(
        0,
        DATA_TYPE_LABELS.indexOf(currentParams.basicSettings.dataType)
      ),
      calibration_period_sp:
        parseInt(currentParams.basicSettings.autoCalibrationPeriod, 10) ||
        base.calibration_period_sp,
      cleaning_algorithm_sp:
        CLEANING_ALGO_REVERSE[currentParams.cleaningAlgorithm] ?? 0,
      hyper_p_iterations_sp:
        Number(currentParams.hyperparameters.iterations) || 0,
      hyper_p_threshold_sp:
        Number(currentParams.hyperparameters.mutationThreshold) || 0,
      hyper_p_size_sp:
        Number(currentParams.hyperparameters.populationSize) || 0,
      hyper_p_chaosfactor_sp:
        Number(currentParams.hyperparameters.chaosFactor) || 0,
      hyper_p_stepsize_sp:
        Number(currentParams.hyperparameters.simulationStepSize) || 0,
      limit_cod_sp: Number(currentParams.effluentConstraints.cod) || 0,
      limit_nh3_n_sp: Number(currentParams.effluentConstraints.nh3n) || 0,
      limit_tp_sp: Number(currentParams.effluentConstraints.tp) || 0,
      limit_tn_sp: Number(currentParams.effluentConstraints.tn) || 0,
      limit_ss_sp: Number(currentParams.effluentConstraints.ss) || 0,
      cleaning_objects_sp: [],
    };

    DEVIATION_MAPPING.forEach(({ front, backend }) => {
      const item = currentParams.deviationSettings[front];
      payload[backend] = item.enabled ? Number(item.value) || 0 : 0;
    });

    payload.cleaning_objects_sp = (
      Object.keys(CLEANING_OBJECT_FRONT_TO_BACK) as CleaningObjectKey[]
    )
      .filter((frontKey) => currentParams.cleaningObjects[frontKey])
      .map((frontKey) => CLEANING_OBJECT_FRONT_TO_BACK[frontKey]);

    delete (payload as any).ts;
    delete (payload as any).update_time_sp;

    return payload;
  }

  function getBackendSnapshot(): BackendSystemParams | null {
    return backendSnapshot.value ? { ...backendSnapshot.value } : null;
  }

  function extractPredictHours(label: string): number {
    // 将前端显示值映射到后端值
    if (label in FRONT_TO_BACK_PREDICT_HOURS) {
      return FRONT_TO_BACK_PREDICT_HOURS[label];
    }
    // 兼容旧格式（如果存在）
    const match = label.match(/(\d+)\s*(?:小时|h)/i);
    return match ? Number(match[1]) : BACKEND_FIELD_DEFAULTS.predict_steps_sp;
  }

  function extractSimIntervalMinutes(label: string): number {
    const hourMatch = label.match(/(\d+)\s*(?:小时|h)/i);
    if (hourMatch) {
      return Number(hourMatch[1]) * 60;
    }
    const minuteMatch = label.match(/(\d+)\s*(?:分钟|min)/i);
    if (minuteMatch) {
      return Number(minuteMatch[1]);
    }
    return BACKEND_FIELD_DEFAULTS.simulate_interval_sp;
  }

  loadFromLocalStorage();

  return {
    params,
    getParams,
    updateParams,
    resetParams,
    saveToLocalStorage,
    loadFromLocalStorage,
    applyBackendParams,
    buildBackendPayload,
    getBackendSnapshot,
    predictAlgorithm,
    extractPredictHours,
    extractSimIntervalMinutes,
  };
});
