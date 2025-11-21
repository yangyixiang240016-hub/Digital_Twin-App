// 系统参数相关接口封装
import http from "./http";

export interface SystemParamsApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
}

export interface BackendSystemParams {
  predict_algorithm_sp: number;
  predict_steps_sp: number;
  simulate_interval_sp: number;
  data_type_sp: number;
  calibration_period_sp: number;
  optimize_algorithm_sp: string;
  cleaning_algorithm_sp: number;
  tolerance_cod_sp: number;
  tolerance_snhx_sp: number;
  tolerance_xtss_sp: number;
  tolerance_tp_sp: number;
  tolerance_tn_sp: number;
  tolerance_do_1_1_sp: number;
  tolerance_do_1_2_sp: number;
  tolerance_do_2_1_sp: number;
  tolerance_do_2_2_sp: number;
  hyper_p_iterations_sp: number;
  hyper_p_threshold_sp: number;
  hyper_p_size_sp: number;
  hyper_p_chaosfactor_sp: number;
  hyper_p_stepsize_sp: number;
  cleaning_objects_sp: string[];
  limit_cod_sp: number;
  limit_nh3_n_sp: number;
  limit_tp_sp: number;
  limit_tn_sp: number;
  limit_ss_sp: number;
  ts?: string;
  update_time_sp?: string | null;
  [extra: string]: any;
}

export type BackendSystemParamsPayload = Partial<BackendSystemParams> & {
  predict_algorithm_sp?: number;
};

export async function getSystemParams(): Promise<
  SystemParamsApiResponse<BackendSystemParams | null>
> {
  const { data } = await http.get<
    SystemParamsApiResponse<BackendSystemParams | null>
  >("/system-params");
  return data;
}

export async function updateSystemParams(
  payload: BackendSystemParamsPayload
): Promise<SystemParamsApiResponse<BackendSystemParams | null>> {
  const { data } = await http.post<
    SystemParamsApiResponse<BackendSystemParams | null>
  >("/system-params", payload);
  return data;
}

/**
 * 兼容旧接口：获取当前预测算法
 */
export async function getPredictAlgorithm(): Promise<{
  success: boolean;
  algorithm: "arima" | "transformer";
  value: number;
  message: string;
}> {
  const response = await http.get("/system-params/predict-algorithm");
  return response.data;
}

/**
 * 兼容旧接口：更新预测算法
 */
export async function updatePredictAlgorithm(
  algorithm: "arima" | "transformer"
): Promise<{
  success: boolean;
  message: string;
}> {
  const { data } = await http.post("/system-params/predict-algorithm", {
    algorithm,
  });
  return data;
}
