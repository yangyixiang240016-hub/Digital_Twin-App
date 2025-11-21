<template>
  <div class="flow-ball">
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="wave-svg">
      <defs>
        <clipPath id="wave-clip">
          <circle cx="50" cy="50" r="50" />
        </clipPath>
      </defs>
      <g clip-path="url(#wave-clip)">
        <path class="wave-path" :d="wavePath" fill="rgba(0, 234, 255, 0.4)" />
      </g>
    </svg>
    <div class="bubbles">
      <span v-for="n in 6" :key="n" :style="bubbleStyle(n)" class="bubble" />
    </div>
    <div class="value">
      {{ typeof value === "number" ? value.toFixed(0) : "0" }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";

const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 200000 },
});

const amplitude = 4; // 波浪高度
const frequency = 2; // 波浪频率
const phase = ref(0);
const wavePath = computed(() => {
  let d = "M 0 50 ";
  for (let x = 0; x <= 100; x++) {
    const y =
      amplitude * Math.sin((x / 100) * frequency * 2 * Math.PI + phase.value);
    d += `L ${x} ${50 - y} `;
  }
  d += "L 100 100 L 0 100 Z";
  return d;
});

onMounted(() => {
  setInterval(() => {
    phase.value += 0.25;
  }, 50);
});

const bubbleStyle = (index) => {
  const delay = Math.random() * 4;
  const size = Math.random() * 6 + 4;
  const left = Math.random() * 90 + 5;
  return {
    animationDelay: `${delay}s`,
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
  };
};
</script>

<style scoped>
.flow-ball {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  background: radial-gradient(circle at center, #003e5a 0%, #001a26 100%);
  border: 2px solid #00eaff;
  box-shadow: 0 0 8px rgba(0, 234, 255, 0.5);
}

.wave-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.bubbles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 2;
}

.bubble {
  position: absolute;
  bottom: 0;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  animation: rise 5s infinite ease-in;
}

@keyframes rise {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translateY(-120px) scale(0.5);
    opacity: 0;
  }
}

.value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  z-index: 3;
  text-shadow: 0 0 6px #00eaff;
}
</style>
