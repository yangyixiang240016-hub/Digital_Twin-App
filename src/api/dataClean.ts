// 数据清洗相关接口封装
import http from "./http";

/**
 * 获取数据清洗数据
 * @param startTime 开始时间，格式：'YYYY-MM-DD HH:MM:SS'
 * @param endTime 结束时间，格式：'YYYY-MM-DD HH:MM:SS'
 * @returns 返回包含整十分钟时间点数据的响应
 */
export async function getCleaningData(
  startTime: string,
  endTime: string
): Promise<{
  success: boolean;
  data: Array<{
    ts: string;
    influent_tol_q_cd: number | null; // 总进水量
    aao_influent_q_cd: number | null; // AAO流量
    mbr_influent_q_cd: number | null; // MBR流量
    aao_influent_1_1_tcod_cd: number | null; // COD
    aao_influent_1_1_snhx_cd: number | null; // NH3-N
    aao_influent_1_1_tn_cd: number | null; // TN
    aao_influent_1_1_tp_cd: number | null; // TP
  }>;
  count: number;
  message: string;
}> {
  const { data } = await http.post("/data-clean/get-data", {
    start_time: startTime,
    end_time: endTime,
  });
  return data;
}

/**
 * 获取原始数据
 * @param startTime 开始时间，格式：'YYYY-MM-DD HH:MM:SS'
 * @param endTime 结束时间，格式：'YYYY-MM-DD HH:MM:SS'
 * @returns 返回包含整十分钟时间点原始数据的响应
 */
export async function getRawData(
  startTime: string,
  endTime: string
): Promise<{
  success: boolean;
  data: Array<{
    ts: string;
    influent_tol_q_cd: number | null; // 总进水量
    aao_influent_q_cd: number | null; // AAO流量
    mbr_influent_q_cd: number | null; // MBR流量
    aao_influent_1_1_tcod_cd: number | null; // COD
    aao_influent_1_1_snhx_cd: number | null; // NH3-N
    aao_influent_1_1_tn_cd: number | null; // TN
    aao_influent_1_1_tp_cd: number | null; // TP
  }>;
  count: number;
  message: string;
}> {
  const { data } = await http.post("/data-clean/get-raw-data", {
    start_time: startTime,
    end_time: endTime,
  });
  return data;
}

/**
 * 获取字段信息
 * @returns 返回字段映射关系
 */
export async function getFieldsInfo(): Promise<{
  success: boolean;
  data: {
    table_name: string;
    fields: Record<string, string>;
  };
  message: string;
}> {
  const { data } = await http.get("/data-clean/fields-info");
  return data;
}
