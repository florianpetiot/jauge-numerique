<template>
  <button
    :class="['rounded-button', { 'has-icon': hasIcon }]"
    :style="buttonStyle"
    @click="$emit('click')"
    type="button"
  >
    <span v-if="hasIcon" class="icon" aria-hidden="true">
      <slot name="icon">
        <img v-if="props && props.iconSrc" :src="props.iconSrc" alt="" class="icon-img" />
        <i v-else-if="icon" :class="icon"></i>
      </slot>
    </span>
    <span class="label"><slot>{{ label }}</slot></span>
  </button>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  icon: { type: String, default: '' },
  iconSrc: { type: String, default: '' },
  color: { type: String, default: '#3273dc' },
  textColor: { type: String, default: '#ffffff' },
  radius: { type: [Number, String], default: 12 },
  paddingY: { type: [Number, String], default: '0.55rem' },
  paddingX: { type: [Number, String], default: '1rem' },
})

const slots = useSlots()
const hasIconSlot = computed(() => !!slots.icon)
const hasIcon = computed(() => !!props.icon || !!props.iconSrc || hasIconSlot.value)

const buttonStyle = computed(() => ({
  backgroundColor: props.color,
  color: props.textColor,
  borderRadius: typeof props.radius === 'number' ? props.radius + 'px' : String(props.radius),
  padding: `${props.paddingY} ${props.paddingX}`,
  border: 'none',
}))
</script>

<style scoped>
.rounded-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
  width: 100%;
}
.rounded-button:active {
    transform: translateY(1px);
}
.rounded-button .icon {
    display: inline-flex; 
    align-items: center; 
    justify-content: center; 
}
.rounded-button .icon i {
    font-style: normal;
}
.rounded-button.has-icon .label {
    margin-left: 0;
    font-size:large
}
.rounded-button .icon-img {
  width: auto;
  height: 1.6em;
  object-fit: contain;
  display: inline-block;
}
</style>
