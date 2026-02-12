<template>
  <main>
    <AppHeader :header-scale="0.6" />

    <section class="threading-container">
      <div v-if="photo" class="content">
        <div class="photo-display" ref="photoDisplayRef">
            <div class="cache-up"></div>
            <div class="cache-down"></div>
            <div class="lines">
                <div v-for="i in numberOfLines" :key="i" class="line"></div>
            </div>
            <img
              ref="zoomImgRef"
              :src="photo"
              alt="Photo capturée"
              :style="imgStyle"
              @touchstart="onTouchStart"
              @touchmove="onTouchMove"
              @touchend="onTouchEnd"
              @touchcancel="onTouchEnd"
            />
        </div>

        <div class="explanations">
          <div>
            <h2>Etape 2</h2>
            <p>Allignez les repères bleus avec le filletage de votre pièce. Commencez par alligner un sommet de droite avec le premier repère.</p>
          </div>

          <div class="controllers">
            <div class="controller">
              <p>Nombre de repères</p>
              <div class="increments">
                <div class="minus" @click="decreaseLines">-</div>
                <!-- <div class="separator"></div> -->
                <div class="plus" @click="increaseLines">+</div>
              </div>
            </div>
            <div class="controller">
              <p>Largeur des repères</p>
              <div class="increments">
                <div class="minus" :class="{ active: minusActive }"
                  @mousedown="startDecreaseLinesWidth"
                  @mouseup="stopWidthRepeat"
                  @mouseleave="stopWidthRepeat"
                  @touchstart.prevent="startDecreaseLinesWidth"
                  @touchend="stopWidthRepeat"
                  @touchcancel="stopWidthRepeat"
                  @contextmenu.prevent
                >-</div>
                <!-- <span>{{ linesWidth }}</span> -->
                <div class="plus " :class="{ active: plusActive }"
                  @mousedown="startIncreaseLinesWidth"
                  @mouseup="stopWidthRepeat"
                  @mouseleave="stopWidthRepeat"
                  @touchstart.prevent="startIncreaseLinesWidth"
                  @touchend="stopWidthRepeat"
                  @touchcancel="stopWidthRepeat"
                  @contextmenu.prevent
                >+</div>
              </div>
            </div>
          </div>
    
          <img :src="example2" alt="Image agrandie">
          
          <div class="footer">
            <!-- <RoundedButton class="back-button" color="#6b6969" :icon-src="backArrow" :to="'/Diameter'" /> -->
            <div class="back-button" @click="goBackToDiameter">
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

    <Toast :message="errorMessage" :show="showError" color="error" @close="showError = false" />
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useImageTransform } from '@/components/useImageTransform';
import AppHeader from '@/components/AppHeader.vue';
import RoundedButton from '@/components/RoundedButton.vue';
import example2 from '@/assets/example2.png';
import backArrow from '@/assets/back_arrow.png';
import Toast from '@/components/Toast.vue';

const photo = ref<string | null>(null);
const analysis = ref<any>(null);
const router = useRouter();

const errorMessage = ref<string>('');
const showError = ref<boolean>(false);
const showErrorToast = (message: string) => {
  errorMessage.value = message;
  showError.value = true;
};

const photoDisplayRef = ref<HTMLElement | null>(null);
const zoomImgRef = ref<HTMLImageElement | null>(null);

const {
  matrixState,
  isAutoAnimating,
  getMatrix,
  setMatrix,
  decomposeMatrix,
  imgStyle,
  waitForImageReady,
  animateMatrix,
} = useImageTransform();

const clamp = (v: number, a = 0.5, b = 5) => Math.max(a, Math.min(b, v));

const autoZoomToCenterPoint = async () => {
  const host = photoDisplayRef.value;
  const img = zoomImgRef.value;
  if (!host || !img) return;

  const hostRect = host.getBoundingClientRect();
  const containerCenter = { x: hostRect.width / 2, y: hostRect.height / 2 };

  // Point de focus (modifie-le plus tard si besoin)
  // Prefer a stored focus point from Diameter (image-local coords)
  let focusPoint = { x: img.clientWidth / 2, y: img.clientHeight / 2 };
  try {
    const raw = sessionStorage.getItem('threadFocus');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (typeof parsed.x === 'number' && typeof parsed.y === 'number') {
        focusPoint = { x: parsed.x, y: parsed.y };
      }
    }
  } catch (e) {
    console.warn('Impossible de lire threadFocus depuis sessionStorage', e);
  }

  const start = getMatrix();
  const { scale: startScale, angle } = decomposeMatrix(start);

  // Zoom supplémentaire contrôlé, sans permettre à l'utilisateur de re-zoomer ensuite
  const targetScale = clamp(startScale * 3, 0.5, 5);
  const rad = angle * Math.PI / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);

  const a = cos * targetScale;
  const b = sin * targetScale;
  const c = -sin * targetScale;
  const d = cos * targetScale;

  // On choisit e,f pour centrer focusPoint dans le container
  const e = containerCenter.x - (a * focusPoint.x + c * focusPoint.y);
  const f = containerCenter.y - (b * focusPoint.x + d * focusPoint.y);

  const target = new DOMMatrix([a, b, c, d, e, f]);
  await animateMatrix(start, target, 700);
};

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

  // Attendre que l'image soit réellement prête (dimensions stables) puis auto-zoom animé
  await waitForImageReady(zoomImgRef.value);
  await autoZoomToCenterPoint();
});


async function nextPage() {

  let width_of_thread_px = 0;
  const host = photoDisplayRef.value;
  if (host) {
    const containerW = host.clientWidth;
    width_of_thread_px = linesWidth.value / 100 * containerW;
  }

  // try {
  //   const res = await fetch(`${import.meta.env.VITE_API_URL}/api/threading`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify({
  //       number_of_threads: numberOfLines.value,
  //       width_of_thread: width_of_thread_px,
  //     }),
  //   });

  //   const json = await res.json().catch(() => ({}));
  //   if (!res.ok || json.error) {
  //     const serverMessage = json.error || 'Erreur inconnue du serveur.';
  //     showErrorToast(`Erreur serveur: ${serverMessage}`);
  //     return;
  //   }
  // }
  // catch (e) {
  //   console.warn('Erreur lors de l\'appel à /api/threading', e);
  //   showErrorToast('Erreur de communication avec le serveur. Veuillez réessayer.');
  //   return;
  // }

  // get width of .lines in pixels
  let linesWidthPx = 0;
  if (host) { 
    const containerW = host.clientWidth;
    linesWidthPx = (linesWidth.value / 100) * containerW;
    linesWidthPx = linesWidthPx / decomposeMatrix(getMatrix()).scale; // prendre en compte le zoom actuel linesWidthPx = realLinesWidthPx;
  }
  
  try {
    sessionStorage.setItem('analysisResult',
    JSON.stringify({
      ...(analysis.value || {}),
      'threading_width_px': linesWidthPx, 
      'threading_number_of_threads': numberOfLines.value
    })); 

    const analysisValue = analysis.value;
    const diameter_mm = analysisValue?.mm_per_pixel * analysisValue?.threading_height_px
    const threading_lenght_mm = analysisValue?.mm_per_pixel * linesWidthPx;

    console.warn({...(analysis.value || {}), 'threading_width_px': linesWidthPx, 'threading_number_of_threads': numberOfLines.value, 'diameter_mm': diameter_mm, 'threading_lenght_mm': threading_lenght_mm});

  } catch (err) { 
    console.warn('Impossible de sauvegarder analysisResult avec threading data', err);
  }

  // Sauvegarder la matrice finale (après auto-zoom) pour l'animation dans Results
  try {
    sessionStorage.setItem('threadingFinalMatrix', JSON.stringify(matrixState.value));
  } catch (err) {
    console.warn('Impossible de sauvegarder threadingFinalMatrix', err);
  }

  router.push({ name: 'Results' });
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

let panActive = false;
let panStartTouch: Vec2 = { x: 0, y: 0 };
let panStartMatrix = new DOMMatrix();

function onTouchStart(e: TouchEvent) {
  if (isAutoAnimating.value) return;
  const touches = e.touches;
  if (touches.length !== 1) {
    panActive = false;
    return;
  }
  const t = touches.item(0);
  if (!t) return;
  panActive = true;
  panStartTouch = getLocalPoint(t);
  panStartMatrix = getMatrix();
}

function onTouchMove(e: TouchEvent) {
  if (isAutoAnimating.value) return;
  const touches = e.touches;
  // On bloque tout zoom/dézoom/rotation: multi-touch ignoré
  if (touches.length !== 1) return;

  if (panActive) {
    const t = touches.item(0);
    if (!t) return;
    const p = getLocalPoint(t);
    // Autoriser uniquement le déplacement horizontal: ignorer dy
    const dx = p.x - panStartTouch.x;
    const next = new DOMMatrix().translate(dx, 0).multiply(panStartMatrix);
    setMatrix(next);
    return;
  }
}

function onTouchEnd(e: TouchEvent) {
  if (isAutoAnimating.value) return;
  const touches = e.touches;
  if (touches.length === 1) {
    const t = touches.item(0);
    if (!t) return;
    panActive = true;
    panStartTouch = getLocalPoint(t);
    panStartMatrix = getMatrix();
    return;
  }
  panActive = false;
}


// CONTROLE DES REPERES
const numberOfLines = ref(8);
const linesWidth = ref(60);
const lineWidth = 4; // px

function increaseLines() {
  const containerW = photoDisplayRef.value?.clientWidth || 420;
  const currentSpacingPx = (linesWidth.value / 100 * containerW - numberOfLines.value * lineWidth) / (numberOfLines.value - 1);
  const newLinesWidthPx = (numberOfLines.value + 1) * lineWidth + numberOfLines.value * currentSpacingPx;
  const newLinesWidthPercent = (newLinesWidthPx / containerW) * 100;
  if (newLinesWidthPercent <= 80) {
    linesWidth.value = Math.min(80, newLinesWidthPercent);
  }
  numberOfLines.value++;
}

function decreaseLines() {
  if (numberOfLines.value > 2) {
    // Recalculate width to keep spacing constant
    const containerW = photoDisplayRef.value?.clientWidth || 420;
    const currentSpacingPx = (linesWidth.value / 100 * containerW - numberOfLines.value * lineWidth) / (numberOfLines.value - 1);
    const newLinesWidthPx = (numberOfLines.value - 1) * lineWidth + (numberOfLines.value - 2) * currentSpacingPx;
    const newLinesWidthPercent = (newLinesWidthPx / containerW) * 100;
    linesWidth.value = Math.max(0, newLinesWidthPercent);
    numberOfLines.value--;
  }
}

function increaseLinesWidth() {
  linesWidth.value = Math.min(80, linesWidth.value + 0.5);
}
function decreaseLinesWidth() {
  linesWidth.value = Math.max(0, linesWidth.value - 0.5);
}

// Repeat-on-hold support
let widthTimer: number | null = null;
let widthInterval: number | null = null;
const minusActive = ref(false);
const plusActive = ref(false);

function startIncreaseLinesWidth() {
  plusActive.value = true;
  increaseLinesWidth();
  if (widthTimer) return;
  widthTimer = window.setTimeout(() => {
    widthInterval = window.setInterval(increaseLinesWidth, 80);
    widthTimer = null;
  }, 400);
}

function startDecreaseLinesWidth() {
  minusActive.value = true;
  decreaseLinesWidth();
  if (widthTimer) return;
  widthTimer = window.setTimeout(() => {
    widthInterval = window.setInterval(decreaseLinesWidth, 80);
    widthTimer = null;
  }, 400);
}

function stopWidthRepeat() {
  minusActive.value = false;
  plusActive.value = false;
  if (widthTimer) {
    clearTimeout(widthTimer);
    widthTimer = null;
  }
  if (widthInterval) {
    clearInterval(widthInterval);
    widthInterval = null;
  }
}



const goHome = () => router.push({ name: 'Home' });
const goToCamera = () => router.push({ name: 'Camera' });

const goBackToDiameter = () => {
  // Sauvegarder l'état courant (même si on ne passe pas par Results)
  try {
    sessionStorage.setItem('threadingFinalMatrix', JSON.stringify(matrixState.value));
  } catch (err) {
    console.warn('Impossible de sauvegarder threadingFinalMatrix', err);
  }

  router.push({ name: 'Diameter' });
};


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

    .threading-container {
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

    .photo-display .lines {
        position: absolute;
        bottom: 0;
        left: 20%;
        width: v-bind(linesWidth + '%');
        height: 60%;
        pointer-events: none;
        z-index: 2;
        display: flex;
        justify-content: space-between;

    }

    .photo-display .lines .line {
        border-left: v-bind(lineWidth + 'px') solid;
        border-image: linear-gradient(to bottom, #00c2d000 0%, #00C3D0 25%, #00C3D0 100%) 1;
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


    .explanations .controllers {
        width: 70%;
        align-self: center;
    }

    .explanations .controller {
        display: flex;
        justify-content: space-between;
        height: 2rem;
        margin: 0.5rem 0;
    }

    .explanations .controller p {
        margin: 0;
        align-self: center;
    }

    .explanations .controller .increments {
        display: flex;
        width: 5rem;
        font-weight: 300;
    }
    
    .explanations .controller .increments .minus,
    .explanations .controller .increments .plus{
        background-color: #ececec;
        height: 100%;
        width: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        user-select: none;
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
    }

    .explanations .controller .increments .minus {
        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
        border-right: 1px solid #b5b5b5;
    }
    .explanations .controller .increments .plus {
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
    }


    .explanations .controller .increments button {
        -webkit-tap-highlight-color: transparent;
        outline: none;
    }

    .explanations .controller .increments .minus:active,
    .explanations .controller .increments .plus:active,
    .explanations .controller .increments .minus.active,
    .explanations .controller .increments .plus.active {
        background-color: #d4d4d4;
    }

    .explanations img {
        width: 70%;
        height: auto;
        align-self: center;
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
