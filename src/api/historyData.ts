// 历史数据相关接口封装
import http from "./http";

/**
 * 查询历史数据
 * @param startDate 开始日期，格式：'YYYY-MM-DD'
 * @param endDate 结束日期，格式：'YYYY-MM-DD'
 * @returns 返回包含每天0点数据的响应
 */
export async function queryHistoryData(
  startDate: string,
  endDate: string
): Promise<{
  success: boolean;
  data: Array<{
    ts: string;
    总进水量: number | null;
    AAO流量: number | null;
    MBR流量: number | null;
    COD: number | null;
    "NH3-N": number | null;
    TN: number | null;
    TP: number | null;
  }>;
  count: number;
  message: string;
}> {
  const { data } = await http.post("/history-data/query", {
    start_date: startDate,
    end_date: endDate,
  });
  return data;
}

/**
 * 查询清洗过的历史数据
 * @param startDate 开始日期，格式：'YYYY-MM-DD'
 * @param endDate 结束日期，格式：'YYYY-MM-DD'
 * @returns 返回包含每天0点清洗数据的响应
 */
export async function queryCleanedHistoryData(
  startDate: string,
  endDate: string
): Promise<{
  success: boolean;
  data: Array<{
    ts: string;
    总进水量: number | null;
    AAO流量: number | null;
    MBR流量: number | null;
    COD: number | null;
    "NH3-N": number | null;
    TN: number | null;
    TP: number | null;
  }>;
  count: number;
  message: string;
}> {
  const { data } = await http.post("/history-data/query-cleaned", {
    start_date: startDate,
    end_date: endDate,
  });
  return data;
}

