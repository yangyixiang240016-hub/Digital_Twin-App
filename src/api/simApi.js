// src/api/simApi.js
import axios from "axios";

const simApi = axios.create({
  baseURL: import.meta.env.VITE_SIM_API_BASE || "http://192.168.3.91:8000",
  timeout: 20000,
});

// 可选：统一错误信息
simApi.interceptors.response.use(
  (res) => res,
  (err) => {
    // 把后端返回的文字错误抛出去，便于前端文案展示
    const msg = err?.response?.data?.message || err?.message || "Network Error";
    return Promise.reject(new Error(msg));
  }
);

export default simApi;
