// src/api/http.ts
import axios from "axios";

export const coreApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE, // 继续给 /api/... 用（你现有代码）
  timeout: 15000,
});

export const altApi = axios.create({
  baseURL: "/alt", // 关键：走 Vite 代理，避免浏览器 CORS
  timeout: 0, // 不设置超时，允许长时间运行的请求（如离线预测）
});

// 可选：简单的响应拦截，抛出 message 便于上层 toast
[coreApi, altApi].forEach((ins) => {
  ins.interceptors.response.use(
    (res) => res,
    (err) => {
      // 让上层能拿到更清晰的错误信息
      err.__msg = err.response?.data?.message || err.message || "请求失败";
      return Promise.reject(err);
    }
  );
});

const http = axios.create({
  baseURL: "/api", // ⭐ 关键：走 Vite 代理，避免跨域
  timeout: 30000,
});

// 你也可以在这里加拦截器做错误提示等
export default http;
