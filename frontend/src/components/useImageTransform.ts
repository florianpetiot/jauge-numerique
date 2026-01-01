import { ref, computed } from 'vue';

// Types exportés pour réutilisation
export type Matrix2D = { a: number; b: number; c: number; d: number; e: number; f: number };

export function useImageTransform() {
  // États réactifs
  const matrixState = ref<Matrix2D>({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 });
  const isAutoAnimating = ref(false);

  // Fonctions utilitaires
  const getMatrix = () => {
    const m = matrixState.value;
    return new DOMMatrix([m.a, m.b, m.c, m.d, m.e, m.f]);
  };

  const setMatrix = (m: DOMMatrix) => {
    matrixState.value = { a: m.a, b: m.b, c: m.c, d: m.d, e: m.e, f: m.f };
  };

  const decomposeMatrix = (m: DOMMatrix) => {
    const scale = Math.hypot(m.a, m.b) || 1;
    const angle = Math.atan2(m.b, m.a) * 180 / Math.PI;
    return { x: m.e, y: m.f, scale, angle };
  };

  // Computed pour le style de l'image
  const imgStyle = computed(() => {
    const m = matrixState.value;
    return {
      transform: `matrix(${m.a}, ${m.b}, ${m.c}, ${m.d}, ${m.e}, ${m.f})`,
      transformOrigin: '0 0'
    };
  });

  // Fonction d'attente pour l'image
  const waitForImageReady = async (imgElement: HTMLImageElement | null) => {
    if (!imgElement) return;
    if (imgElement.complete && imgElement.naturalWidth > 0) return;
    await new Promise<void>((resolve) => {
      const onLoad = () => {
        imgElement.removeEventListener('load', onLoad);
        imgElement.removeEventListener('error', onError);
        resolve();
      };
      const onError = () => {
        imgElement.removeEventListener('load', onLoad);
        imgElement.removeEventListener('error', onError);
        resolve();
      };
      imgElement.addEventListener('load', onLoad, { once: true });
      imgElement.addEventListener('error', onError, { once: true });
    });
  };

  // Fonction d'animation de matrice
  const animateMatrix = async (from: DOMMatrix, to: DOMMatrix, durationMs = 350) => {
    isAutoAnimating.value = true;
    const start = performance.now();
    const easeInOut = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);

    await new Promise<void>((resolve) => {
      const step = (now: number) => {
        const t = Math.min(1, (now - start) / durationMs);
        const k = easeInOut(t);

        const m = new DOMMatrix([
          from.a + (to.a - from.a) * k,
          from.b + (to.b - from.b) * k,
          from.c + (to.c - from.c) * k,
          from.d + (to.d - from.d) * k,
          from.e + (to.e - from.e) * k,
          from.f + (to.f - from.f) * k,
        ]);
        setMatrix(m);

        if (t < 1) {
          requestAnimationFrame(step);
          return;
        }
        resolve();
      };

      requestAnimationFrame(step);
    });

    isAutoAnimating.value = false;
  };

  // Retourner tout ce qui est nécessaire
  return {
    matrixState,
    isAutoAnimating,
    getMatrix,
    setMatrix,
    decomposeMatrix,
    imgStyle,
    waitForImageReady,
    animateMatrix,
  };
}