// AAO离线模拟API服务
import http from "./http";

export interface SimulationRequest {
  start_time: string;
  end_time: string;
  data_source: number;
}

export interface SimulationResponse {
  success: boolean;
  message?: string;
  data?: any;
}

export class AAOSimulationService {
  private baseUrl = "/alt"; // 使用Vite代理路径 - 用于AAO模拟相关API
  private apiBaseUrl = "/api"; // 用于查询数据库的API

  /**
   * 启动AAO离线模拟
   */
  async startAAOSimulation(
    request: SimulationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/ManualSimulate/AAO/`;
      console.log("=== AAO模拟请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("baseUrl:", this.baseUrl);
      console.log("完整请求信息:", {
        url,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("响应URL:", response.url);
        console.error(
          "响应头:",
          Object.fromEntries(response.headers.entries())
        );
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        // 如果是JSON格式，正常解析
        data = await response.json();
      } else {
        // 如果不是JSON格式，获取文本内容
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        // 尝试解析为JSON，如果失败则返回文本
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          // 如果解析失败，将文本作为消息返回
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("AAO模拟启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动MBR离线模拟
   */
  async startMBRSimulation(
    request: SimulationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/ManualSimulate/MBR/`;
      console.log("=== MBR模拟请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("baseUrl:", this.baseUrl);
      console.log("完整请求信息:", {
        url,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("响应URL:", response.url);
        console.error(
          "响应头:",
          Object.fromEntries(response.headers.entries())
        );
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        // 如果是JSON格式，正常解析
        data = await response.json();
      } else {
        // 如果不是JSON格式，获取文本内容
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        // 尝试解析为JSON，如果失败则返回文本
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          // 如果解析失败，将文本作为消息返回
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("MBR模拟启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 停止AAO模拟
   */
  async stopAAOSimulation(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/ManualSimulateStop/AAO/`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        // 如果是JSON格式，正常解析
        data = await response.json();
      } else {
        // 如果不是JSON格式，获取文本内容
        const text = await response.text();
        console.log("停止模拟后端返回的文本内容:", text);

        // 尝试解析为JSON，如果失败则返回文本
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          // 如果解析失败，将文本作为消息返回
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("停止AAO模拟失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 停止MBR模拟
   */
  async stopMBRSimulation(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/ManualSimulateStop/MBR/`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        // 如果是JSON格式，正常解析
        data = await response.json();
      } else {
        // 如果不是JSON格式，获取文本内容
        const text = await response.text();
        console.log("停止模拟后端返回的文本内容:", text);

        // 尝试解析为JSON，如果失败则返回文本
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          // 如果解析失败，将文本作为消息返回
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("停止MBR模拟失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取最新离线模拟结果
   */
  async getLatestOfflineResult(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/offline/result/latest`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("获取最新离线模拟结果失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取离线模拟结果数据
   */
  async getOfflineResultData(params?: {
    start_time?: string;
    end_time?: string;
    limit?: number;
  }): Promise<SimulationResponse> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.start_time)
        queryParams.append("start_time", params.start_time);
      if (params?.end_time) queryParams.append("end_time", params.end_time);
      if (params?.limit) queryParams.append("limit", params.limit.toString());

      const url = `${this.apiBaseUrl}/offline/result/data${
        queryParams.toString() ? "?" + queryParams.toString() : ""
      }`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("获取离线模拟结果数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取模拟结果图表数据
   */
  async getSimulationResultChartData(params: {
    start_time: string;
    end_time: string;
    field_names?: string[];
  }): Promise<SimulationResponse> {
    try {
      const url = `${this.apiBaseUrl}/offline/result/chart-data`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: {
          data: data.data,
          times: data.times,
        },
        message: data.message,
      };
    } catch (error) {
      console.error("获取模拟结果图表数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取优化结果图表数据
   */
  async getOptimizationResultChartData(params: {
    start_time: string;
    end_time: string;
    field_names?: string[];
  }): Promise<SimulationResponse> {
    try {
      const url = `${this.apiBaseUrl}/offline/result/optimization-chart-data`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: {
          data: data.data,
          realtime_data: data.realtime_data,
          times: data.times,
        },
        message: data.message,
      };
    } catch (error) {
      console.error("获取优化结果图表数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 根据开始时间获取离线模拟结果数据
   */
  async getOfflineResultByStartTime(start_time: string): Promise<SimulationResponse> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append("start_time", start_time);

      const url = `${this.apiBaseUrl}/offline/result/by-start-time?${queryParams.toString()}`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("根据开始时间获取离线模拟结果数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动AAO在线优化
   */
  async startAAOOnlineOptimization(): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/OnlineAutoOptimizeStart/AAO/`;
      console.log("=== AAO在线优化请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("================================");

      const response = await fetch(url, {
        method: "GET",
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("AAO在线优化启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动MBR在线优化
   */
  async startMBROnlineOptimization(): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/OnlineAutoOptimizeStart/MBR/`;
      console.log("=== MBR在线优化请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("================================");

      const response = await fetch(url, {
        method: "GET",
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("MBR在线优化启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动AAO在线模拟
   */
  async startAAOOnlineSimulation(
    request: OnlineSimulationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/OnlineSimulate/AAO/`;
      console.log("=== AAO在线模拟请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("AAO在线模拟启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动MBR在线模拟
   */
  async startMBROnlineSimulation(
    request: OnlineSimulationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/OnlineSimulate/MBR/`;
      console.log("=== MBR在线模拟请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("MBR在线模拟启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取字段映射信息
   */
  async getFieldMappings(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/offline/result/fields`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("获取字段映射信息失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动AAO离线优化
   */
  async startAAOOptimization(
    request: OptimizationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/AutoOptimize/AAO/`;
      console.log("=== AAO优化请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("响应URL:", response.url);
        console.error(
          "响应头:",
          Object.fromEntries(response.headers.entries())
        );
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("AAO优化启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 启动MBR离线优化
   */
  async startMBROptimization(
    request: OptimizationRequest
  ): Promise<SimulationResponse> {
    try {
      const url = `${this.baseUrl}/AutoOptimize/MBR/`;
      console.log("=== MBR优化请求调试信息 ===");
      console.log("请求URL:", url);
      console.log("请求数据:", request);
      console.log("================================");

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        console.error("=== HTTP错误详情 ===");
        console.error("状态码:", response.status);
        console.error("状态文本:", response.statusText);
        console.error("响应URL:", response.url);
        console.error(
          "响应头:",
          Object.fromEntries(response.headers.entries())
        );
        console.error("================================");
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }

      // 检查响应内容类型
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("MBR优化启动失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 停止AAO优化
   */
  async stopAAOOptimization(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/AutoOptimizeStop/AAO/`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("停止AAO优化后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("停止AAO优化失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 停止MBR优化
   */
  async stopMBROptimization(): Promise<SimulationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/AutoOptimizeStop/MBR/`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("停止优化后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("停止MBR优化失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取AAO优化进度
   */
  async getAAOOptimizationProgress(): Promise<SimulationResponse> {
    try {
      const response = await fetch(
        `${this.baseUrl}/AutoOptimizeProgress/AAO/`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("获取AAO优化进度后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("获取AAO优化进度失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 根据开始时间获取离线优化结果数据
   */
  async getOptimizationResultByStartTime(start_time: string): Promise<SimulationResponse> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append("start_time", start_time);

      const url = `${this.apiBaseUrl}/offline/optimization/by-start-time?${queryParams.toString()}`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("根据开始时间获取离线优化结果数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取在线模拟结果数据（最新一条）
   */
  async getOnlineSimulationResultByStartTime(start_time?: string): Promise<SimulationResponse> {
    try {
      // start_time参数已废弃，不再使用，但保留以兼容旧接口
      const url = `${this.apiBaseUrl}/online/simulation/by-start-time`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("根据开始时间获取在线模拟结果数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取在线优化结果数据（最新一条）
   */
  async getOnlineOptimizationResultByStartTime(start_time?: string): Promise<SimulationResponse> {
    try {
      // start_time参数已废弃，不再使用，但保留以兼容旧接口
      const url = `${this.apiBaseUrl}/online/optimization/by-start-time`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // 检查后端返回的业务状态
      if (!data.success) {
        return {
          success: false,
          message: data.error || data.message || "获取数据失败",
          data: null,
        };
      }

      return {
        success: true,
        data: data.data,
        message: data.message,
      };
    } catch (error) {
      console.error("根据开始时间获取在线优化结果数据失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }

  /**
   * 获取MBR优化进度
   */
  async getMBROptimizationProgress(): Promise<SimulationResponse> {
    try {
      const response = await fetch(
        `${this.baseUrl}/AutoOptimizeProgress/MBR/`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.log("获取MBR优化进度后端返回的文本内容:", text);

        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = {
            message: text,
            rawResponse: text,
          };
        }
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("获取MBR优化进度失败:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "未知错误",
      };
    }
  }
}

// 在线模拟请求接口
export interface OnlineSimulationRequest {
  data_source: number; // 0-原始数据 1-清洗后数据 2-化验室数据
  forecast_step: number; // 预测步长
  frequency: number; // 运行频率(分钟)
}

// 优化请求接口
export interface OptimizationRequest {
  start_time: string;
  end_time: string;
  frequency: number;
  PSO_iter?: number;
  size?: number;
  mpc_steps?: number;
  aao_config_name?: string;
  mbr_config_name?: string;
  optimize_algorithm_sp?: string;
}

// 导出单例实例
export const aaoSimulationService = new AAOSimulationService();
