import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";
import moment from "moment";
import { useSimulationParamsStore } from "./useSimulationParamsStore";

// 1. 出水参数类型：只检测这五项
type ParamKey = "cod" | "nh3n" | "tn" | "tp" | "ss";

// 2. 报警项结构
interface AlarmItem {
  time: string; // 格式化时间
  content: string; // 报警内容（如“出水COD超标”）
  value: string; // 报警数值（保留两位小数）
}

// 3. 实时出水数据接口返回格式（仅包含检测项）
type OutflowData = Partial<Record<ParamKey, number>>;

// 5. 对应参数的中文名，用于报警内容拼接
const labelMap: Record<ParamKey, string> = {
  cod: "COD",
  nh3n: "NH3-N",
  tn: "TN",
  tp: "TP",
  ss: "SS",
};

// 6. 定义 Pinia 报警监测 store
export const useAlarmStore = defineStore("alarm", () => {
  const alarmList = ref<AlarmItem[]>([]);
  const simulationParamsStore = useSimulationParamsStore();

  const getDesignLimit = (key: ParamKey): number => {
    const constraints = simulationParamsStore.params.effluentConstraints;
    const fallback: Record<ParamKey, number> = {
      cod: 30,
      nh3n: 2,
      tn: 15,
      tp: 0.4,
      ss: 8,
    };
    const val = constraints[key];
    const num = Number(val);
    return Number.isFinite(num) ? num : fallback[key];
  };

  /**
   * 实时检查出水是否有超标项，符合就加入 alarmList
   */
  async function checkOutflowAlarm(): Promise<void> {
    try {
      const res = await axios.get<OutflowData>("/api/realtime/outflow/quality");
      const data = res.data;
      const time = moment().format("MM-DD HH:mm");

      (Object.keys(labelMap) as ParamKey[]).forEach((key) => {
        const val = data[key];
        const limit = getDesignLimit(key);
        if (val !== undefined && limit !== undefined && val > limit) {
          alarmList.value.push({
            time,
            content: `出水${labelMap[key]}超标`,
            value: val.toFixed(2),
          });
        }
      });
    } catch (e) {
      console.warn("🚨 报警数据获取失败:", e);
    }
  }

  /**
   * 清空报警列表
   */
  function clearAlarms(): void {
    alarmList.value = [];
  }

  return {
    alarmList,
    checkOutflowAlarm,
    clearAlarms,
  };
});
