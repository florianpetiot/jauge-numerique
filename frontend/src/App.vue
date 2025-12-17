<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue';

function setVh() {
  const vv = (window as any).visualViewport;
  const height = vv && typeof vv.height === 'number' ? vv.height : window.innerHeight;
  const vh = height * 0.01; // 1% of viewport height in px
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

let resizeHandler = () => setVh();

onMounted(() => {
  setVh();
  window.addEventListener('resize', resizeHandler);
  window.addEventListener('orientationchange', resizeHandler);
  if ((window as any).visualViewport) {
    (window as any).visualViewport.addEventListener('resize', resizeHandler);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler);
  window.removeEventListener('orientationchange', resizeHandler);
  if ((window as any).visualViewport) {
    (window as any).visualViewport.removeEventListener('resize', resizeHandler);
  }
});
</script>

<template>
  <router-view />
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
</style>

<style scoped></style>
