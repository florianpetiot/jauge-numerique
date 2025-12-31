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
              @touchstart.passive="onTouchStart"
              @touchmove.passive="onTouchMove"
              @touchend.passive="onTouchEnd"
              @touchcancel.passive="onTouchEnd"
            />
        </div>

        <div class="explanations">
            <RoundedButton label="Nouvelle photo" :icon-src="camera" color="#B3741D" :to="'/camera'" />
    
            <h2>Etape 1</h2>
            <p>Agrandissez votre image pour faire correspondre le diamètre du filetage à la zone bleutée.</p>
    
            <img :src="example1" alt="Image agrandie">
    
            <div class="footer">
              <RoundedButton class="next-button" label="Suivant" color="#09BC8A" @click="nextWithZoom" />
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
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '@/components/AppHeader.vue';
import RoundedButton from '@/components/RoundedButton.vue';
import camera from '@/assets/camera.png';
import example1 from '@/assets/example1.png';

const photo = ref<string | null>(null);
const analysis = ref<any>(null);
const router = useRouter();

const photoDisplayRef = ref<HTMLElement | null>(null);
const zoomImgRef = ref<HTMLImageElement | null>(null);

type Matrix2D = { a: number; b: number; c: number; d: number; e: number; f: number };
const matrixState = ref<Matrix2D>({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 });

const getMatrix = () => {
  const m = matrixState.value;
  return new DOMMatrix([m.a, m.b, m.c, m.d, m.e, m.f]);
};

const setMatrix = (m: DOMMatrix) => {
  matrixState.value = { a: m.a, b: m.b, c: m.c, d: m.d, e: m.e, f: m.f };
};

const decomposeMatrix = (m: DOMMatrix) => {
  // Hypothèse: scale uniforme + rotation (ce que nos gestes produisent)
  const scale = Math.hypot(m.a, m.b) || 1;
  const angle = Math.atan2(m.b, m.a) * 180 / Math.PI;
  return { x: m.e, y: m.f, scale, angle };
};

const imgStyle = computed(() => {
  const m = matrixState.value;
  return {
    transform: `matrix(${m.a}, ${m.b}, ${m.c}, ${m.d}, ${m.e}, ${m.f})`,
    // Origine stable (top-left) => notre matrice est exprimée dans le repère du container
    transformOrigin: '0 0'
  };
});

const clamp = (v: number, a = 0.5, b = 5) => Math.max(a, Math.min(b, v));

onMounted(async () => {
  // Restore previous transform (priorité à la matrice)
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
        matrixState.value = parsed;
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
        const m = new DOMMatrix().translate(x, y).rotate(angle).scale(scale);
        setMatrix(m);
      }
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

async function nextWithZoom() {
  const m = getMatrix();
  const { x, y, scale, angle } = decomposeMatrix(m);

  try {
    sessionStorage.setItem('transformMatrix', JSON.stringify(matrixState.value));
    // On conserve aussi l'ancien format pour compat/debug
    sessionStorage.setItem('transform', JSON.stringify({ x, y, scale, angle }));
  } catch (err) {
    console.warn('Impossible de sauvegarder transform', err);
  }

  try {
    const res = await fetch('/api/diameter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        // analysis: analysis.value,
        transform: {
          x,
          y,
          scale,
          angle,
          matrix: matrixState.value
        }
      })
    });
  } catch (e) {
    console.warn('Erreur lors de l\'appel à /api/diameter', e);
  }

  // Calculate thread focus point: bottom center of the visible target rectangle
  try {
    const host = photoDisplayRef.value;
    if (host) {
      const rect = host.getBoundingClientRect();
      const cx = rect.width / 2;
      // target has CSS height: 30% and centered at 50% => bottom at 50% + 15% = 65%
      const by = rect.height * 0.65;

      // transform container point -> image local coordinates using inverse matrix
      const m = getMatrix();
      try {
        const inv = m.inverse();
        const p = inv.transformPoint(new DOMPoint(cx, by));
        sessionStorage.setItem('threadFocus', JSON.stringify({ x: p.x, y: p.y }));
      } catch (inner) {
        console.warn('Impossible d\'inverser la matrice pour calculer threadFocus', inner);
      }
    }
  } catch (err) {
    console.warn('Erreur en calculant threadFocus', err);
  }

  router.push({ name: 'Threading' });
}

// --- Gestion tactile native ---
type Vec2 = { x: number; y: number };

const getLocalPoint = (t: Touch): Vec2 => {
  const host = photoDisplayRef.value;
  const rect = host?.getBoundingClientRect();
  if (!rect) return { x: t.clientX, y: t.clientY };
  return { x: t.clientX - rect.left, y: t.clientY - rect.top };
};

const midpoint = (p1: Vec2, p2: Vec2): Vec2 => ({
  x: (p1.x + p2.x) / 2,
  y: (p1.y + p2.y) / 2,
});

const distance = (p1: Vec2, p2: Vec2) => Math.hypot(p2.x - p1.x, p2.y - p1.y);

const angleDeg = (p1: Vec2, p2: Vec2) =>
  Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;

let panActive = false;
let panStartTouch: Vec2 = { x: 0, y: 0 };
let panStartMatrix = new DOMMatrix();

let gestureActive = false;
let gestureStartDistance = 0;
let gestureStartAngle = 0;
let gestureStartMidpoint: Vec2 = { x: 0, y: 0 };
let gestureStartScale = 1;
let gestureStartMatrix = new DOMMatrix();

function resetFromTouches(e: TouchEvent) {
  const touches = e.touches;
  if (touches.length === 1) {
    const t = touches.item(0);
    if (!t) return;
    gestureActive = false;
    panActive = true;
    panStartTouch = getLocalPoint(t);
    panStartMatrix = getMatrix();
  } else if (touches.length >= 2) {
    const t1 = touches.item(0);
    const t2 = touches.item(1);
    if (!t1 || !t2) return;
    panActive = false;
    gestureActive = true;
    const p1 = getLocalPoint(t1);
    const p2 = getLocalPoint(t2);
    gestureStartDistance = distance(p1, p2) || 1;
    gestureStartAngle = angleDeg(p1, p2);
    gestureStartMidpoint = midpoint(p1, p2);

    gestureStartMatrix = getMatrix();
    gestureStartScale = Math.hypot(gestureStartMatrix.a, gestureStartMatrix.b) || 1;
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
    const p = getLocalPoint(t);
    const dx = p.x - panStartTouch.x;
    const dy = p.y - panStartTouch.y;
    const next = new DOMMatrix().translate(dx, dy).multiply(panStartMatrix);
    setMatrix(next);
    return;
  }

  if (touches.length >= 2) {
    // si on passe de 1 doigt -> 2 doigts en cours de route
    if (!gestureActive) resetFromTouches(e);
    if (!gestureActive) return;

    const t1 = touches.item(0);
    const t2 = touches.item(1);
    if (!t1 || !t2) return;

    const p1 = getLocalPoint(t1);
    const p2 = getLocalPoint(t2);

    // pinch
    const dist = distance(p1, p2) || gestureStartDistance || 1;
    const rawRatio = dist / (gestureStartDistance || 1);
    const desiredScale = clamp(gestureStartScale * rawRatio);
    const ratio = desiredScale / (gestureStartScale || 1);

    // rotation
    const a = angleDeg(p1, p2);
    const rotDelta = a - gestureStartAngle;

    // centre du geste (dans le repère du container)
    const mid = midpoint(p1, p2);

    // Matrice incrémentale exacte: on force le zoom+rotation autour du midpoint de départ,
    // puis on amène ce midpoint au midpoint courant.
    const inc = new DOMMatrix()
      .translate(mid.x, mid.y)
      .rotate(rotDelta)
      .scale(ratio)
      .translate(-gestureStartMidpoint.x, -gestureStartMidpoint.y);

    const next = inc.multiply(gestureStartMatrix);
    setMatrix(next);
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
      /* Hauteur stable entre les écrans, indépendante du contenu sous l'image */
      height: 40%;
      min-height: 240px;
      flex: 0 0 auto;
      touch-action: none;
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

    .explanations h2 {
        font-size:xx-large;
    }

    .explanations img {
        width: 70%;
        align-self: center;
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

    .footer {
      padding: 0 2rem;
    }
</style>
