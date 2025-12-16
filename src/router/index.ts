import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/home.vue'),
    },
    {
      path: '/camera',
      name: 'Camera',
      component: () => import('../views/Camera.vue'),
    },
  ],
})

export default router
