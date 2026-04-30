<template>
  <main class="desktop-message-container">
    <div class="header-wrapper">
      <AppHeader :header-scale="0.8" />
    </div>
    
    <section class="hero">
      <div class="icon-container">
        <span class="device-icon">📱</span>
      </div>
      
      <div class="content-wrapper">
        <h1 class="title">Expérience Mobile Uniquement</h1>
        <p class="subtitle">
          Cette jauge numérique est conçue spécifiquement pour analyser des filetages en utilisant l'appareil photo de votre smartphone.
        </p>
        <p class="instruction">
          Veuillez ouvrir ce site depuis votre téléphone mobile pour utiliser le service.
        </p>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<style scoped>
.desktop-message-container {
  min-height: 100vh;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', 'Roboto', sans-serif;
  color: #1a1a1a;
  box-sizing: border-box;
}

.header-wrapper {
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  border-bottom: 1px solid #f8f9fa;
}

.hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.icon-container {
  margin-bottom: 2.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.device-icon {
  font-size: 4rem;
  background: #ffffff;
  width: 8rem;
  height: 8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.title {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin: 0;
  color: #222222;
}

.subtitle {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555555;
  margin: 0;
  font-weight: 400;
}

.instruction {
  font-size: 1.05rem;
  font-weight: 600;
  color: #B3741D;
  background-color: rgba(179, 116, 29, 0.1);
  padding: 1.2rem 2rem;
  border-radius: 16px;
  margin-top: 1rem;
  box-shadow: 0 4px 12px rgba(179, 116, 29, 0.05);
}
</style>
