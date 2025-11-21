export type OfflineMode = "dynamic" | "steady";
export type OptimizeMode = "manual" | "auto";

export interface RunPayload {
  mode: OfflineMode;
  optMode: OptimizeMode;
  data: any;
  params: Record<string, number>;
  objectives: Record<string, number>;
  bounds: Record<string, { min: number; max: number }>;
}

export interface StartPayload {
  selection: {
    process: string;
    mode: string;
  };
  data?: any;
  params?: any;
  objectives?: any;
  bounds?: any;
}

export interface TaskInfo {
  taskId: string;
  status: "running" | "done" | "error" | "cancelled";
  progress: number;
  message?: string;
}

export interface ResultData {
  kpi: any;
  charts: any;
  tables: any[];
  metadata?: any;
}
