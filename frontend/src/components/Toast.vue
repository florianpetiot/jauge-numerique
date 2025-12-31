<template>
  <transition name="toast">
    <div v-if="show" class="toast" :style="{ backgroundColor: computedColor }">
      {{ message }}
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';

interface Props {
  message: string;
  color?: string;
  show: boolean;
  duration?: number;
}

const props = withDefaults(defineProps<Props>(), {
  color: 'error',
  duration: 3000,
});

const emit = defineEmits<{
  close: [];
}>();

const computedColor = computed(() => {
  switch (props.color) {
    case 'error':
      return '#ff4444';
    case 'success':
      return '#4caf50';
    case 'warning':
      return '#ff9800';
    case 'info':
      return '#2196f3';
    default:
      return props.color.startsWith('#') ? props.color : '#ff4444';
  }
});

// Auto-hide after duration when show becomes true
watch(() => props.show, (newShow) => {
  if (newShow) {
    setTimeout(() => {
      emit('close');
    }, props.duration);
  }
});
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  z-index: 1000;
  max-width: 90%;
  word-wrap: break-word;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease-out;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>