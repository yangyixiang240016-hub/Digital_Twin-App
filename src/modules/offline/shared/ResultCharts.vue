<template>
  <div class="charts">
    <div class="box">
      <h3>Effluent quality comparison</h3>
      <table class="tbl">
        <thead>
          <tr>
            <th>Index</th>
            <th>Baseline</th>
            <th>Sim/Optimized</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="k in ['COD', 'TN', 'NH3N', 'TP', 'NO3', 'pH', 'Turbidity']"
            :key="k"
          >
            <td>{{ k }}</td>
            <td>{{ baseline?.[k] ?? "-" }}</td>
            <td>{{ result?.[k] ?? "-" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="box">
      <h3>Key parameters (before vs after)</h3>
      <table class="tbl">
        <thead>
          <tr>
            <th>Param</th>
            <th>Before</th>
            <th>After</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in params" :key="p.k">
            <td>{{ p.name }}</td>
            <td>{{ before?.[p.k] ?? "-" }}</td>
            <td>{{ after?.[p.k] ?? "-" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  baseline: Object,
  result: Object,
  before: Object,
  after: Object,
});
const params = [
  { k: "aerZone1", name: "Aeration Zone 1 (Nm³/d)" },
  { k: "aerZone2", name: "Aeration Zone 2 (Nm³/d)" },
  { k: "aerZone3", name: "Aeration Zone 3 (Nm³/d)" },
  { k: "aerZone4", name: "Aeration Zone 4 (Nm³/d)" },
  { k: "MLR", name: "MLR Return Flow (m³/d)" },
  { k: "RAS", name: "RAS Return Flow (m³/d)" },
  { k: "SAS", name: "SAS Sludge Rate (m³/d)" },
  { k: "PAC", name: "PAC dosage (mg/L)" },
];
</script>

<style scoped>
.charts {
  display: grid;
  gap: 12px;
}
.box {
  border: 1px solid #e5e7eb;
  padding: 12px;
  border-radius: 12px;
}
.tbl {
  width: 100%;
  border-collapse: collapse;
}
.tbl th,
.tbl td {
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  text-align: left;
}
</style>
