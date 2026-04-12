<template>
  <main class="accueil">
    <div class="header-container">
      <AppHeader :header-scale="0.8" />
    </div>

    <section class="hero">
      <div class="content-wrapper">
        <h1 class="title">Mesure de Précision</h1>
        <p class="subtitle">
          Photographiez un filetage et obtenez son diamètre et son pas de manière automatique et instantanée.
        </p>
      </div>
      
      <div class="features">
        <div class="feature-item">
          <div class="feature-icon">✨</div>
          <span>Analyse rapide</span>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📏</div>
          <span>Haute précision</span>
        </div>
      </div>

      <div class="action-container">
        <RoundedButton 
          label="Nouvelle photo" 
          :iconSrc="camera" 
          color="#B3741D" 
          textColor="#ffffff"
          radius="15px"
          paddingY="1rem"
          paddingX="2rem"
          :to="'/camera'" 
          class="main-cta"
        />
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import RoundedButton from '@/components/RoundedButton.vue'
import AppHeader from '@/components/AppHeader.vue'
import camera from '@/assets/camera.png'
</script>

<style scoped>
.accueil {
  min-height: calc(var(--vh, 1vh) * 100);
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', 'Roboto', sans-serif;
  color: #1a1a1a;
  box-sizing: border-box;
}

.header-container {
  padding: 1rem;
  display: flex;
  justify-content: center;
}

.hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem 3rem;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin: 0;
  color: #222222;
}

.subtitle {
  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  line-height: 1.6;
  color: #555555;
  max-width: 500px;
  margin: 0;
  font-weight: 400;
}

.features {
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  flex-wrap: wrap;
  margin: 3rem 0 auto;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  color: #666666;
  font-size: 0.95rem;
  font-weight: 500;
}

.feature-icon {
  font-size: 1.6rem;
  background: #f8f9fa;
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.action-container {
  margin-top: 3rem;
  width: 100%;
  max-width: 300px;
}

.main-cta {
  box-shadow: 0 6px 18px rgba(179, 116, 29, 0.25);
  font-size: 1.1rem;
  width: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.main-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(179, 116, 29, 0.35);
}

@media (min-width: 768px) {
  .header-container {
    padding-top: 2rem;
  }
}
</style>
