<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, computed } from 'vue';

const isLandscape = ref(false);
const isMobile = ref(false);

const showOrientationMessage = computed(() => isMobile.value && isLandscape.value);

function setVh() {
  const vv = (window as any).visualViewport;
  const height = vv && typeof vv.height === 'number' ? vv.height : window.innerHeight;
  const vh = height * 0.01; // 1% of viewport height in px
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

function checkDevice() {
  isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
}

function checkOrientation() {
  isLandscape.value = window.innerWidth > window.innerHeight;
}

let resizeHandler = () => {
  setVh();
  checkOrientation();
  checkDevice();
};

let orientationHandler = () => {
  checkOrientation();
};

let wheelHandler = (e: WheelEvent) => {
  if (e.ctrlKey) {
    e.preventDefault();
  }
};

onMounted(() => {
  checkDevice();
  checkOrientation();
  setVh();
  window.addEventListener('resize', resizeHandler);
  window.addEventListener('orientationchange', orientationHandler);
  if ((window as any).visualViewport) {
    (window as any).visualViewport.addEventListener('resize', resizeHandler);
  }
  // Prevent zoom on PC
  window.addEventListener('wheel', wheelHandler, { passive: false });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler);
  window.removeEventListener('orientationchange', orientationHandler);
  if ((window as any).visualViewport) {
    (window as any).visualViewport.removeEventListener('resize', resizeHandler);
  }
  window.removeEventListener('wheel', wheelHandler);
});
</script>

<template>
  <div v-if="showOrientationMessage" class="orientation-message">
    Veuillez tourner votre téléphone en mode portrait pour une meilleure expérience.
  </div>
  <router-view v-else />
</template>

<style>
html, body, #app {
  /* use the computed --vh so mobile address bar is accounted for */
  height: calc(var(--vh, 1vh) * 100);
  margin: 0;
  overflow: hidden; /* prevent page scroll when address bar retracts */
}
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
#app {
  min-height: calc(var(--vh, 1vh) * 100);
}
.orientation-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  text-align: center;
  color: white;
  background: rgba(0, 0, 0, 0.6);
  padding: 20px;
  border-radius: 10px;
  z-index: 1000;
}
</style>

<style scoped></style>
