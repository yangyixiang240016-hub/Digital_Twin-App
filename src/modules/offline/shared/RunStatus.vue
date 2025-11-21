<template>
  <div class="status">
    <div v-if="loading" class="loading">Simulation in progress...</div>
    <div v-else-if="taskId" class="ok">Task: {{ taskId }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ loading: boolean; taskId: string | null }>();
</script>

<style scoped>
.loading {
  padding: 12px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
}
.ok {
  padding: 8px 12px;
  border-radius: 8px;
  background: #ecfdf5;
  border: 1px solid #bbf7d0;
}
</style>
