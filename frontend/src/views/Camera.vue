<template>
    <main>
        <AppHeader :header-scale="0.6" />

        <section class="camera-container">
            <div class="video-wrapper">
                <div class="cache-up"></div>
                <div class="cache-down"></div>
                <div class="overlay">
                    <div class="threading">Placez votre<br>filetage ici</div>
                    <div class="coin">Placez une<br>pièce de<br>monnaie ici</div>
                </div>
                <video ref="videoRef" autoplay playsinline></video>
            </div>

            <div class="shutter" :class="{ disabled: isUploading }" @click="captureAndNext">
                <div class="first-circle"></div>
                <div class="second-circle"></div>
            </div>
        </section>
    </main>
</template>


<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '@/components/AppHeader.vue';

const videoRef = ref<HTMLVideoElement | null>(null);
const router = useRouter();
let stream: MediaStream | null = null;
const isUploading = ref(false);

const startCamera = async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
        if (videoRef.value) {
            videoRef.value.srcObject = stream;
            await videoRef.value.play();
        }
    } catch (err) {
        console.error('Erreur accès caméra:', err);
        alert('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
    }
};

const stopCamera = () => {
    if (stream) {
        stream.getTracks().forEach((t) => t.stop());
        stream = null;
    }
    if (videoRef.value) videoRef.value.srcObject = null;
};

const captureAndNext = async () => {
    if (!videoRef.value || isUploading.value) return;
    isUploading.value = true;
    const video = videoRef.value;
    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) { isUploading.value = false; return; }
    ctx.drawImage(video, 0, 0, width, height);
    const photo = canvas.toDataURL('image/jpeg', 0.92);

    // Timeout helper
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000); // 10s

    try {
        // Utilise URL relative pour passer par le proxy Vite en dev
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: photo }),
            signal: controller.signal
        });
        clearTimeout(timeout);

        const json = await res.json().catch(() => ({}));
        if (!res.ok || !json.success) {
            console.error('Erreur serveur:', json);
            alert('Erreur lors de l\'analyse de l\'image sur le serveur.');
            isUploading.value = false;
            return;
        }

        try {
            sessionStorage.setItem('capturedPhoto', photo);
            sessionStorage.setItem('analysisResult', JSON.stringify(json));
        } catch (e) {
            console.warn('Impossible de sauvegarder en sessionStorage', e);
        }

        stopCamera();
        router.push({ name: 'Home' });
    } catch (e: any) {
        if (e.name === 'AbortError') {
            console.error('Timeout contacting analysis server');
            alert('Le serveur met trop de temps à répondre.');
        } else {
            console.error('Erreur réseau:', e);
            alert('Impossible de contacter le serveur d\'analyse.');
        }
        isUploading.value = false;
    }
};

onMounted(() => {
    startCamera();
});

onBeforeUnmount(() => {
    stopCamera();
});

</script>


<style scoped>
    main {
        min-height: 100vh;
        box-sizing: border-box;
        background-color: #fff;
        padding: 2rem 0 0 0;
        text-align: center;
        color: black;
        font-family: 'Inter', 'Roboto';
    }

/* MOBILE FIRST */
    main {
        height: 100vh;
        margin: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .camera-container {
        width: 100%;
        max-width: 420px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: center;
        flex: 1 1 auto;
        justify-content: space-between;
        padding: 0;
        box-sizing: border-box;
    }

    .video-wrapper {
        width: 100%;
        background: #000;
        overflow: hidden;
        position: relative;
        flex: 1 1 auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .video-wrapper .cache-up,
    .video-wrapper .cache-down {
        position: absolute;
        left: 0;
        right: 0;
        width: 100%;
        height: 12%;
        pointer-events: none;
        z-index: 3;
    }

    .video-wrapper .cache-up {
        top: 0;
        background: linear-gradient(to bottom, #fff, #ffffff00);
    }

    .video-wrapper .cache-down {
        bottom: 0;
        background: linear-gradient(to top, #fff, #ffffff00);
    }

    .video-wrapper .overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 2;
        background-color: #0000005b;
        color: #fff;
    }

    .video-wrapper .overlay .threading {
        position: absolute;
        width: 100%;
        height: 30%;
        top: 17%;
        border-top: 2px solid #fff;
        border-bottom: 2px solid #fff;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }

    .video-wrapper .overlay .coin {
        position: absolute;
        bottom: 17%;
        left: 50%;
        transform: translateX(-50%);
        width: 33%;
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        border: 2px solid #fff;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }

    video {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
        position: relative;
        z-index: 1;
    }

    .shutter {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 12px rgba(0,0,0,0.7);
        cursor: pointer;
        position: relative;
        margin: 1rem 0;
        flex: 0 0 auto;
        transition: opacity 0.2s ease;
    }

    .shutter.disabled {
        opacity: 0.6;
        pointer-events: none;
    }

    .first-circle {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 2px solid #000;
    }

    .second-circle {
        position: absolute;
        width: 80%;
        height: 80%;
        border-radius: 50%;
        border: 3px solid #000;
    }

    .primary { background: #2563eb; color: #fff; }
    .secondary { background: #efefef; color: #111; }

    .hidden { display: none; }

    .photo-preview img {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

</style>