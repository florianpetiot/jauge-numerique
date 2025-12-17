<template>
  <main>
    <AppHeader :header-scale="0.6" />

    <section class="diameter-container">
      <div v-if="photo" class="content">
        <div class="photo-display" ref="photoDisplayRef">
            <div class="cache-up"></div>
            <div class="cache-down"></div>
            <div class="target"></div>
            <img
              ref="zoomImgRef"
              :src="photo"
              alt="Photo capturée"
              :style="imgStyle"
              @touchstart.prevent="onTouchStart"
              @touchmove.prevent="onTouchMove"
              @touchend.prevent="onTouchEnd"
              @touchcancel.prevent="onTouchEnd"
            />
        </div>

        <div class="explanations">
            <RoundedButton label="Nouvelle photo" :icon-src="camera" color="#B3741D" :to="'/camera'" />
    
            <h2>Etape 1</h2>
            <p>Agrandissez votre image pour faire correspondre le diamètre du filetage à la zone bleutée.</p>
    
            <img :src="example1" alt="Image agrandie">
    
            <RoundedButton label="Suivant" color="#09BC8A" @click="nextWithZoom" />
        </div>
      </div>
      
      
      <div v-else class="no-photo">
        <p>Aucune photo trouvée dans la session.</p>
        <button @click="goToCamera">Retour à la caméra</button>
      </div>


      <!-- <div v-if="analysis" class="analysis">
        <h3>Résultat d'analyse</h3>
        <pre>{{ analysis }}</pre>
      </div>

      <div class="actions">
        <button @click="goHome">Accueil</button>
      </div> -->
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '@/components/AppHeader.vue';
import RoundedButton from '@/components/RoundedButton.vue';
import camera from '@/assets/camera.png';
import example1 from '@/assets/example1.png';

const photo = ref<string | null>(null);
const analysis = ref<any>(null);
const router = useRouter();

const zoomImgRef = ref<HTMLImageElement | null>(null);
const photoDisplayRef = ref<HTMLElement | null>(null);
const x = ref<number>(0);
const y = ref<number>(0);
const scale = ref<number>(1);
const angle = ref<number>(0);

const imgStyle = computed(() => ({
  transform: `translate(${x.value}px, ${y.value}px) rotate(${angle.value}deg) scale(${scale.value})`,
  transformOrigin: 'center center'
}));

const clamp = (v: number, a = 0.5, b = 5) => Math.max(a, Math.min(b, v));

onMounted(async () => {
  // restore previous transform if present
  try {
    const t = sessionStorage.getItem('transform');
    if (t) {
      const parsed = JSON.parse(t);
      x.value = parsed.x || 0;
      y.value = parsed.y || 0;
      scale.value = parsed.scale || 1;
      angle.value = parsed.angle || 0;
    }
  } catch (err) {
    console.warn('Impossible de restaurer transform', err);
  }

  // existing photo loading
  try {
    const p = sessionStorage.getItem('capturedPhoto');
    photo.value = p;
  } catch (e) {
    console.warn('Impossible de lire capturedPhoto depuis sessionStorage', e);
    photo.value = null;
  }

  try {
    const a = sessionStorage.getItem('analysisResult');
    analysis.value = a ? JSON.parse(a) : null;
  } catch (e) {
    console.warn('Impossible de lire analysisResult depuis sessionStorage', e);
    analysis.value = null;
  }

  // wait nextTick so template is rendered and refs (img) are available
  await nextTick();
});

onBeforeUnmount(() => {
  // rien à nettoyer côté interact (gestion native)
});

function nextWithZoom() {
  try {
    sessionStorage.setItem('transform', JSON.stringify({ x: x.value, y: y.value, scale: scale.value, angle: angle.value }));
  } catch (err) {
    console.warn('Impossible de sauvegarder transform', err);
  }
  router.push({ name: 'Home' });
}

// --- Gestion tactile native ---
type Vec2 = { x: number; y: number };

const getMidpoint = (t1: Touch, t2: Touch): Vec2 => ({
  x: (t1.clientX + t2.clientX) / 2,
  y: (t1.clientY + t2.clientY) / 2,
});

const getDistance = (t1: Touch, t2: Touch) => {
  const dx = t2.clientX - t1.clientX;
  const dy = t2.clientY - t1.clientY;
  return Math.hypot(dx, dy);
};

const getAngleDeg = (t1: Touch, t2: Touch) =>
  Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;

let panActive = false;
let panStartTouch: Vec2 = { x: 0, y: 0 };
let panStartTranslate: Vec2 = { x: 0, y: 0 };

let gestureActive = false;
let gestureStartDistance = 0;
let gestureStartAngle = 0;
let gestureStartMidpoint: Vec2 = { x: 0, y: 0 };
let gestureStartScale = 1;
let gestureStartRotation = 0;
let gestureStartTranslate: Vec2 = { x: 0, y: 0 };

function resetFromTouches(e: TouchEvent) {
  const touches = e.touches;
  if (touches.length === 1) {
    const t = touches.item(0);
    if (!t) return;
    gestureActive = false;
    panActive = true;
    panStartTouch = { x: t.clientX, y: t.clientY };
    panStartTranslate = { x: x.value, y: y.value };
  } else if (touches.length >= 2) {
    const t1 = touches.item(0);
    const t2 = touches.item(1);
    if (!t1 || !t2) return;
    panActive = false;
    gestureActive = true;
    gestureStartDistance = getDistance(t1, t2) || 1;
    gestureStartAngle = getAngleDeg(t1, t2);
    gestureStartMidpoint = getMidpoint(t1, t2);

    gestureStartScale = scale.value;
    gestureStartRotation = angle.value;
    gestureStartTranslate = { x: x.value, y: y.value };
  } else {
    panActive = false;
    gestureActive = false;
  }
}

function onTouchStart(e: TouchEvent) {
  resetFromTouches(e);
}

function onTouchMove(e: TouchEvent) {
  const touches = e.touches;
  if (touches.length === 1 && panActive) {
    const t = touches.item(0);
    if (!t) return;
    const dx = t.clientX - panStartTouch.x;
    const dy = t.clientY - panStartTouch.y;
    x.value = panStartTranslate.x + dx;
    y.value = panStartTranslate.y + dy;
    return;
  }

  if (touches.length >= 2) {
    // si on passe de 1 doigt -> 2 doigts en cours de route
    if (!gestureActive) resetFromTouches(e);
    if (!gestureActive) return;

    const t1 = touches.item(0);
    const t2 = touches.item(1);
    if (!t1 || !t2) return;

    // pinch
    const dist = getDistance(t1, t2) || gestureStartDistance || 1;
    const ratio = dist / (gestureStartDistance || 1);
    scale.value = clamp(gestureStartScale * ratio);

    // rotation
    const a = getAngleDeg(t1, t2);
    angle.value = gestureStartRotation + (a - gestureStartAngle);

    // pan (déplacement du centre du geste)
    const mid = getMidpoint(t1, t2);
    x.value = gestureStartTranslate.x + (mid.x - gestureStartMidpoint.x);
    y.value = gestureStartTranslate.y + (mid.y - gestureStartMidpoint.y);
  }
}

function onTouchEnd(e: TouchEvent) {
  // recalibrage quand le nombre de doigts change
  resetFromTouches(e);
}

const goHome = () => router.push({ name: 'Home' });
const goToCamera = () => router.push({ name: 'Camera' });


</script>

<style scoped>
    main {
      min-height: calc(var(--vh, 1vh) * 100);
        box-sizing: border-box;
        background-color: #fff;
        padding: 2rem 0 0 0;
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

    .diameter-container {
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
      flex: 1 1 auto;
      min-height: 0;
      touch-action: none;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #e6e6e6;
      background-image: radial-gradient(circle, #b1b1b1 1.5px, transparent 1.5px);
      background-size: 20px 20px;
    }

    .photo-display img {
      display: block;
      width: 100%;
      height: auto;
      object-fit: contain;
      touch-action: none;
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

    .photo-display .target {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 80%;
        height: 30%;
        background-color: #00c2d033;
        border-top: 3px solid #00c2d0;
        border-bottom: 3px solid #00c2d0;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 4;
    }

    .explanations {
      width: 100%;
      box-sizing: border-box;
      flex: 0 0 auto;
      overflow: auto;
      padding: 0 0.75rem 1rem 0.75rem;
    }

    .explanations h2, .explanations p {
        text-align: left;
    }

    .explanations h2 {
        font-size:xx-large;
    }

    .explanations img {
        width: 70%;
        height: auto;
        margin: 1rem 0;
    }

    .no-photo p {
        margin-bottom: 0.5rem;
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
</style>
