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
                    <h2>Résultats</h2>

                    <!-- Matches found -->
                    <div v-if="matches.length > 0" class="matches">
                        <div
                            v-for="(match, index) in matches"
                            :key="match.id"
                            class="match-card"
                            :class="{ 'primary': index === 0, 'secondary': index === 1 }"
                        >
                            <div class="match-header">
                                <span class="match-name">{{ formatName(match.nom) }}</span>
                                <span class="match-score" :class="scoreClass(match.score)">
                                    {{ match.score }}%
                                </span>
                            </div>
                            <div class="match-details">
                                <div class="detail-row">
                                    <span class="detail-label">Diamètre nominal</span>
                                    <span class="detail-value">{{ match.diam_mm }} mm</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Pas</span>
                                    <span class="detail-value">{{ formatPitch(match) }}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Système</span>
                                    <span class="detail-value">{{ match.unite === 'I' ? 'Impérial' : 'Métrique' }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- No matches -->
                    <div v-else class="no-match">
                        <div class="no-match-icon">🔍</div>
                        <p class="no-match-title">Aucun filetage correspondant</p>
                        <p class="no-match-hint">Les mesures ne correspondent à aucune norme connue. Vérifiez l'alignement et réessayez.</p>
                    </div>

                    <div class="footer">
                        <div class="back-button" @click="router.push({ name: 'Threading' })">
                            <img :src="backArrow" alt="Retour">
                        </div>
                        <RoundedButton label="Nouvelle mesure" color="#09BC8A" @click="goToCamera" />
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
const matches = ref<any[]>([]);
const router = useRouter();
const photoDisplayRef = ref<HTMLElement | null>(null);
const zoomImgRef = ref<HTMLImageElement | null>(null);

const { imgStyle, setMatrix, waitForImageReady, animateMatrix } = useImageTransform();

const formatName = (name: string) => name.replace(/_/g, ' ');

const formatPitch = (match: any) => {
    if (match.unite === 'I') {
        return `${match.pas} TPI (≈ ${match.pitch_mm} mm)`;
    }
    return `${match.pas} mm`;
};

const scoreClass = (score: number) => {
    if (score >= 90) return 'score-high';
    if (score >= 70) return 'score-medium';
    return 'score-low';
};

onMounted(async () => {
    try {
        photo.value = sessionStorage.getItem('capturedPhoto');
    } catch (e) {
        console.warn('Impossible de lire capturedPhoto', e);
        photo.value = null;
    }

    // Charger les résultats de filetage (matches avec scores)
    try {
        const raw = sessionStorage.getItem('threadingResult');
        if (raw) {
            const parsed = JSON.parse(raw);
            matches.value = parsed.matches || [];
        }
    } catch (e) {
        console.warn('Impossible de lire threadingResult', e);
    }

    await nextTick();
    await waitForImageReady(zoomImgRef.value);

    // Animation : départ depuis la matrice Threading → cible matrice Diameter
    let startMatrix = new DOMMatrix();
    try {
        const tm = sessionStorage.getItem('threadingFinalMatrix');
        if (tm) {
            const parsed = JSON.parse(tm);
            if (parsed && typeof parsed.a === 'number' && typeof parsed.b === 'number' &&
                typeof parsed.c === 'number' && typeof parsed.d === 'number' &&
                typeof parsed.e === 'number' && typeof parsed.f === 'number') {
                startMatrix = new DOMMatrix([parsed.a, parsed.b, parsed.c, parsed.d, parsed.e, parsed.f]);
                setMatrix(startMatrix);
            }
        }
    } catch (err) {
        console.warn('Impossible de restaurer threadingFinalMatrix', err);
    }

    let targetMatrix = new DOMMatrix();
    try {
        const tm = sessionStorage.getItem('transformMatrix');
        if (tm) {
            const parsed = JSON.parse(tm);
            if (parsed && typeof parsed.a === 'number' && typeof parsed.b === 'number' &&
                typeof parsed.c === 'number' && typeof parsed.d === 'number' &&
                typeof parsed.e === 'number' && typeof parsed.f === 'number') {
                targetMatrix = new DOMMatrix([parsed.a, parsed.b, parsed.c, parsed.d, parsed.e, parsed.f]);
            }
        } else {
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
        console.warn('Impossible de restaurer transformMatrix', err);
    }

    await animateMatrix(startMatrix, targetMatrix, 700);
});

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

    /* --- Explanations & Results Cards --- */
    .explanations {
        width: 100%;
        box-sizing: border-box;
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 0;
        overflow: auto;
        padding: 0 0.75rem 1rem 0.75rem;
    }

    .explanations h2 {
        text-align: left;
        margin: 0.5rem 0;
        font-size: xx-large;
    }

    .content {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        min-height: 0;
        gap: 1rem;
    }

    /* Match cards */
    .matches {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 100%;
        margin: 0.5rem 0;
    }

    .match-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border-left: 4px solid #cbd5e1;
    }

    .match-card.primary {
        border-left-color: #09BC8A;
        background: linear-gradient(135deg, #f0fdf7, #f8f9fa);
        box-shadow: 0 2px 12px rgba(9, 188, 138, 0.12);
    }

    .match-card.secondary {
        border-left-color: #94a3b8;
        opacity: 0.85;
    }

    .match-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }

    .match-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
    }

    .match-card.primary .match-name {
        font-size: 1.8rem;
    }

    .match-score {
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }

    .score-high { background: #09BC8A; }
    .score-medium { background: #F59E0B; }
    .score-low { background: #94a3b8; }

    .match-details {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
    }

    .detail-label { color: #64748b; }
    .detail-value { font-weight: 500; color: #334155; }

    /* No match */
    .no-match {
        text-align: center;
        padding: 2rem 1rem;
    }

    .no-match-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

    .no-match-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #334155;
        margin: 0.5rem 0;
    }

    .no-match-hint {
        font-size: 0.9rem;
        color: #94a3b8;
        margin: 0;
    }

    .no-photo p { margin-bottom: 0.5rem; }

    /* Footer */
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