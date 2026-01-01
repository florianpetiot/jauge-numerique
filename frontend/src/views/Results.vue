<template>
    <main>
        <AppHeader :header-scale="0.6" />
        <section class="results-container">
            <div v-if="photo" class="content">
                <div class="photo-display" ref="photoDisplayRef">
                    <div class="cache-up"></div>
                    <div class="cache-down"></div>
                    <img
                    ref="zoomImgRef"
                    :src="photo"
                    alt="Photo capturée"
                    :style="imgStyle"
                    />
                </div>

                <div class="explanations">
                <div>
                    <h2>résultats de l'analyse</h2>
                    <p>Ici seront affichés les résultats de l'analyse.</p>
                </div>
                
                <div class="footer">
                    <!-- <RoundedButton class="back-button" color="#6b6969" :icon-src="backArrow" :to="'/Diameter'" /> -->
                    <div class="back-button" @click="router.push({ name: 'Threading' })">
                        <img :src="backArrow" alt="Flèche de retour">
                    </div>
                    <RoundedButton label="Suivant" color="#09BC8A" @click="nextPage" />
                </div>
                </div>
            </div>

            <div v-else class="no-photo">
                <p>Aucune photo trouvée dans la session.</p>
                <button @click="goToCamera">Retour à la caméra</button>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useImageTransform } from '@/components/useImageTransform';
import AppHeader from '@/components/AppHeader.vue';
import RoundedButton from '@/components/RoundedButton.vue';
import backArrow from '@/assets/back_arrow.png';

const photo = ref<string | null>(null);
const router = useRouter();
const photoDisplayRef = ref<HTMLElement | null>(null);
const zoomImgRef = ref<HTMLImageElement | null>(null);

const { imgStyle, setMatrix, waitForImageReady, animateMatrix } = useImageTransform();

onMounted(async () => {
  // existing photo loading
  try {
    const p = sessionStorage.getItem('capturedPhoto');
    photo.value = p;
  } catch (e) {
    console.warn('Impossible de lire capturedPhoto depuis sessionStorage', e);
    photo.value = null;
  }

  // wait nextTick so template is rendered and refs (img) are available
  await nextTick();

  // Attendre que l'image soit réellement prête (dimensions stables)
  await waitForImageReady(zoomImgRef.value);

  // Restaurer la matrice finale de Threading comme point de départ
  let startMatrix = new DOMMatrix();
  try {
    const tm = sessionStorage.getItem('threadingFinalMatrix');
    if (tm) {
      const parsed = JSON.parse(tm);
      if (
        parsed &&
        typeof parsed.a === 'number' && typeof parsed.b === 'number' &&
        typeof parsed.c === 'number' && typeof parsed.d === 'number' &&
        typeof parsed.e === 'number' && typeof parsed.f === 'number'
      ) {
        startMatrix = new DOMMatrix([parsed.a, parsed.b, parsed.c, parsed.d, parsed.e, parsed.f]);
        setMatrix(startMatrix);
      }
    }
  } catch (err) {
    console.warn('Impossible de restaurer threadingFinalMatrix', err);
  }

  // Restaurer la matrice de Diameter comme cible
  let targetMatrix = new DOMMatrix();
  try {
    const tm = sessionStorage.getItem('transformMatrix');
    if (tm) {
      const parsed = JSON.parse(tm);
      if (
        parsed &&
        typeof parsed.a === 'number' && typeof parsed.b === 'number' &&
        typeof parsed.c === 'number' && typeof parsed.d === 'number' &&
        typeof parsed.e === 'number' && typeof parsed.f === 'number'
      ) {
        targetMatrix = new DOMMatrix([parsed.a, parsed.b, parsed.c, parsed.d, parsed.e, parsed.f]);
      }
    } else {
      // Compat: ancien format {x,y,scale,angle}
      const t = sessionStorage.getItem('transform');
      if (t) {
        const parsed = JSON.parse(t);
        const x = typeof parsed.x === 'number' ? parsed.x : 0;
        const y = typeof parsed.y === 'number' ? parsed.y : 0;
        const scale = typeof parsed.scale === 'number' ? parsed.scale : 1;
        const angle = typeof parsed.angle === 'number' ? parsed.angle : 0;
        targetMatrix = new DOMMatrix().translate(x, y).rotate(angle).scale(scale);
      }
    }
  } catch (err) {
    console.warn('Impossible de restaurer transformMatrix pour Results', err);
  }

  // Animer le dézoom de la matrice de départ vers la matrice cible
  await animateMatrix(startMatrix, targetMatrix, 700);
});

const nextPage = () => {
  // TODO: implement next page logic
};

const goToCamera = () => router.push({ name: 'Camera' });

</script>


<style scoped>
    main {
        min-height: calc(var(--vh, 1vh) * 100);
        box-sizing: border-box;
        background-color: #fff;
        padding: 0;
        text-align: center;
        color: black;
        font-family: 'Inter', 'Roboto';
    }

    /* MOBILE FIRST */
    main {
        height: calc(var(--vh, 1vh) * 100);
        margin: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .results-container {
        width: 100%;
        max-width: 420px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        flex: 1 1 auto;
        overflow-x: hidden;
        min-height: 0;
        box-sizing: border-box;
    }

    .photo-display {
      overflow: hidden;
      position: relative;
      width: 100%;
      box-sizing: border-box;
      height: 40%;
      min-height: 240px;
      flex: 0 0 auto;
      touch-action: pan-x;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      background-color: #e6e6e6;
      background-image: radial-gradient(circle, #b1b1b1 1.5px, transparent 1.5px);
      background-size: 20px 20px;
    }

    .photo-display img {
      position: absolute;
      left: 0;
      display: block;
      top: 0;
      width: 100%;
      height: auto;
      object-fit: cover;
      touch-action: pan-x;
      -webkit-user-drag: none;
      user-select: none;
      will-change: transform;
      pointer-events: auto;
    }

    .photo-display .cache-up,
    .photo-display .cache-down {
        position: absolute;
        left: 0;
        right: 0;
        width: 100%;
        height: 12%;
        pointer-events: none;
        z-index: 3;
    }

    .photo-display .cache-up {
        top: 0;
        background: linear-gradient(to bottom, #fff, #ffffff00);
    }

    .photo-display .cache-down {
        bottom: 0;
        background: linear-gradient(to top, #fff, #ffffff00);
    }

    .explanations {
      width: 100%;
      box-sizing: border-box;
      flex: 1 1 auto;
      display: flex;
      flex-direction: column;
      /* align-items: center; */
      justify-content: space-evenly;
      min-height: 0;
      overflow: auto;
      padding: 0 0.75rem 1rem 0.75rem;
    }

    .explanations h2, .explanations p {
        text-align: left;
        margin: 0.5rem 0;
    }

    /* content wrapper fills remaining space after header */
    .content {
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      min-height: 0;
      gap: 1rem;
    }

    .footer {
      display: flex;
      justify-content: space-evenly;
      gap: 1rem;
      margin-top: 1rem;
      padding: 0 2rem;
    }
    
    .footer .back-button {
      background-color: #6b6969;
      flex: 0 0 auto;
      height: 100%;
      aspect-ratio: 1 / 1;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

</style>