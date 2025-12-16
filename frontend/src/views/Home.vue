<template>
  <main class="accueil">

    <AppHeader :header-scale="0.8" />

    <div>
        <p>Photographiez un filetage, obtenez diamètre + pas automatiquement</p>
    </div>

    <div style="margin-top:1.6rem; display:flex; gap:0.8rem; justify-content:center; flex-wrap:wrap;">
      <RoundedButton label="Nouvelle photo" :iconSrc="camera" color="#B3741D" :to="'/camera'" />
      <RoundedButton label="Charger une image" :iconSrc="upload" color="#B3741D" />
    </div>
    
  </main>
</template>

<script setup lang="ts">
import RoundedButton from '../components/RoundedButton.vue'
import AppHeader from '../components/AppHeader.vue'
import camera from '../assets/camera.png'
import upload from '../assets/upload.png'
</script>

<style scoped>
main {
  min-height: 100vh;
  box-sizing: border-box;
  background-color: #fff;
  padding: 2rem 1rem;
  text-align: center;
  color: black;
  font-family: 'Inter', 'Roboto';
}

/* MOBILE FIRST */
main {
  height: 100%;
  margin-bottom: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content:space-around;
}

/* Header moved to src/components/AppHeader.vue */

main p {
  font-size: clamp(1rem, 4vw, 1.2rem);
  max-width: 28rem;
  margin: 0 auto 2rem;
}
.btn-principal {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: #fff;
  color: #333;
  text-decoration: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  transition: transform 0.2s;
}
.btn-principal:hover {
  transform: translateY(-2px);
}


/* TABLETTE/DESKTOP */
@media (min-width: 768px) {
  main {
    padding: 4rem 2rem;
  }
}
</style>
