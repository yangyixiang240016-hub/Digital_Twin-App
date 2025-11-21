<template>
  <table class="tbl" v-if="rows?.length">
    <thead>
      <tr>
        <th v-for="c in cols" :key="c">{{ c }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(r, i) in rows" :key="i">
        <td v-for="c in cols" :key="c">{{ r[c] }}</td>
      </tr>
    </tbody>
  </table>
  <div v-else class="empty">No data</div>
</template>

<script setup lang="ts">
const props = defineProps<{ rows: any[] }>();
const cols = ["time", "COD", "TN", "NH3N", "TP", "NO3", "flow"];
</script>

<style scoped>
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
.empty {
  padding: 12px;
  color: #6b7280;
}
</style>
