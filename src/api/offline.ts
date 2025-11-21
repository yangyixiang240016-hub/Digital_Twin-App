// # 离线相关接口封装（统一 AAO/MBR、模拟/优化）
import http from "./http";
import type {
  StartPayload,
  TaskInfo,
  ResultData,
} from "@/modules/offline/types";

export async function startOffline(payload: StartPayload): Promise<TaskInfo> {
  const { process, mode } = payload.selection;
  // 约定：/offline/{process}/{mode}/start
  const url = `/offline/${process}/${mode}/start`;
  const { data } = await http.post(url, payload);
  return data; // { taskId, status }
}

export async function pollTask(taskId: string): Promise<TaskInfo> {
  const { data } = await http.get(`/offline/task/${taskId}/status`);
  return data;
}

export async function fetchResult(taskId: string): Promise<ResultData> {
  const { data } = await http.get(`/offline/task/${taskId}/result`);
  return data;
}

export async function cancelTask(taskId: string): Promise<TaskInfo> {
  const { data } = await http.post(`/offline/task/${taskId}/cancel`);
  return data;
}

// 新增：直接调用离线模拟API
export async function runOfflineDynamic(
  payload: any
): Promise<{ taskId: string }> {
  const { data } = await http.post("/offline/sim/run", {
    ...payload,
    type: "dynamic",
  });
  return { taskId: data.jobId };
}

export async function runOfflineSteady(
  payload: any
): Promise<{ taskId: string }> {
  const { data } = await http.post("/offline/sim/run", {
    ...payload,
    type: "steady",
  });
  return { taskId: data.jobId };
}

export async function runOfflineOptimize(
  payload: any
): Promise<{ taskId: string }> {
  const { data } = await http.post("/offline/sim/run", {
    ...payload,
    type: payload.mode === "dynamic" ? "dynamic" : "steady",
    func: "optimize",
  });
  return { taskId: data.jobId };
}

export async function fetchOfflineResult(taskId: string): Promise<any> {
  const { data } = await http.get("/offline/sim/result", {
    params: { jobId: taskId },
  });
  return { status: "done", payload: data };
}
