<template>
  <div class="offline-result-display">
    <div class="result-header">
      <h2>离线模拟结果</h2>
      <div class="result-meta">
        <span class="meta-item">
          <strong>工艺类型:</strong> {{ processType }}
        </span>
        <span class="meta-item">
          <strong>模拟类型:</strong> {{ simulationType }}
        </span>
        <span class="meta-item">
          <strong>数据源:</strong> {{ dataSource }}
        </span>
        <span class="meta-item">
          <strong>时间范围:</strong> {{ timeRange }}
        </span>
      </div>
    </div>

    <div class="result-content">
      <div
        v-for="(category, categoryName) in groupedResults"
        :key="categoryName"
        class="result-category"
      >
        <div class="category-title">{{ categoryName }}</div>
        <div class="category-items">
          <div
            v-for="item in category"
            :key="item.fieldName"
            class="result-item"
          >
            <span class="item-label">{{ item.displayName }}:</span>
            <span class="item-value">{{ formatValue(item.value) }}</span>
            <span class="item-unit">{{ item.unit }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { aaoOfflineFieldMappings } from "@/utils/fieldMapping";

interface Props {
  processType: string;
  simulationType: string;
  dataSource: string;
  timeRange: string;
  resultData: Record<string, any>;
}

const props = defineProps<Props>();

// 处理模拟结果数据，按分类分组
const groupedResults = computed(() => {
  if (!props.resultData) return {};

  const grouped: Record<string, any[]> = {};

  // 遍历所有字段映射
  aaoOfflineFieldMappings.forEach((mapping) => {
    const value = props.resultData[mapping.fieldName];
    if (value !== undefined && value !== null) {
      const category = mapping.category || "其他";
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push({
        fieldName: mapping.fieldName,
        displayName: mapping.displayName,
        value: value,
        unit: mapping.unit || "",
      });
    }
  });

  return grouped;
});

// 格式化数值显示
const formatValue = (value: any) => {
  if (typeof value === "number") {
    return value.toFixed(2);
  }
  return value;
};
</script>

<style scoped>
.offline-result-display {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 24px;
  color: #ffffff;
  max-width: 1200px;
  margin: 0 auto;
}

.result-header {
  margin-bottom: 30px;
  text-align: center;
}

.result-header h2 {
  color: #ffffff;
  font-size: 24px;
  margin-bottom: 15px;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.meta-item {
  color: #e5e7eb;
  font-size: 14px;
}

.meta-item strong {
  color: #4f46e5;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-category {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
}

.category-title {
  font-size: 16px;
  color: #4f46e5;
  margin-bottom: 15px;
  font-weight: bold;
  border-bottom: 1px solid rgba(79, 70, 229, 0.3);
  padding-bottom: 8px;
}

.category-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid #4f46e5;
}

.item-label {
  color: #ffffff;
  font-size: 14px;
  flex: 1;
  min-width: 0;
}

.item-value {
  color: #10b981;
  font-size: 14px;
  font-weight: bold;
  min-width: 80px;
  text-align: right;
}

.item-unit {
  color: #6b7280;
  font-size: 12px;
  min-width: 40px;
}

@media (max-width: 768px) {
  .category-items {
    grid-template-columns: 1fr;
  }

  .result-meta {
    flex-direction: column;
    align-items: center;
  }
}
</style>
