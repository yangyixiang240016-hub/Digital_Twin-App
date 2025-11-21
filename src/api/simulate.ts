// src/api/simulate.ts
import { altApi } from "./http";

/**
 * 后端接口（.91）：
 * POST  /BasicSchedule/AAO/
 * GET   /BasicScheduleStop/AAO/
 * POST  /BasicSchedule/MBR/
 * GET   /BasicScheduleStop/MBR/
 */
export async function startAAO() {
  // 如果后端不需要 body，就传空对象
  return altApi.post("/BasicSchedule/AAO/", {});
}

export async function stopAAO() {
  return altApi.get("/BasicScheduleStop/AAO/");
}

export async function startMBR() {
  return altApi.post("/BasicSchedule/MBR/", {});
}

export async function stopMBR() {
  return altApi.get("/BasicScheduleStop/MBR/");
}
