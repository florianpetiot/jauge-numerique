<template>
  <div class="header" :style="{'--header-scale': headerScale}" @click="router.push({ name: 'Home' })">
    <img src="../assets/lmdt.png" alt="Logo LMDT" />
    <div class="bar-vertical"></div>
    <div class="title">
      <h1>Jauge</h1>
      <h1>Numérique</h1>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
const props = defineProps({
  headerScale: { type: [Number, String], default: 1 }
});
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  --header-scale: 1;
  margin-bottom: calc(2rem * var(--header-scale));
  margin-top: calc(2rem * var(--header-scale));
  font-family: 'Inter', 'Roboto';
}

.header img {
  height: calc(80px * var(--header-scale));
  width: auto;
}

.bar-vertical {
  width: calc(3px * var(--header-scale));
  height: calc(80px * var(--header-scale));
  background-color: #333;
  margin: 0 1rem;
}

.header .title h1 {
  margin: 0;
  line-height: 1.2;
}

.header .title h1:first-child {
  font-size: calc(50px * var(--header-scale));
}

.header .title h1:nth-child(2) {
  font-size: calc(27px * var(--header-scale));
}
</style>
