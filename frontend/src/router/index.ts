import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
    },
    {
      path: '/camera',
      name: 'Camera',
      component: () => import('../views/Camera.vue'),
    },
    {
      path: '/diameter',
      name: 'Diameter',
      component: () => import('../views/Diameter.vue'),
    },
    {
      path: '/threading',
      name: 'Threading',
      component: () => import('../views/Threading.vue'),
    },
    {
      path: '/results',
      name: 'Results',
      component: () => import('../views/Results.vue'),
    }
  ],
})

export default router
