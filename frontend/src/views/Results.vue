<template>
    <main>
        <AppHeader :header-scale="0.6" />
        <section class="results-section">
            <h1>Résultats de l'analyse</h1>
            <div class="results-content">
                <p>Ici seront affichés les résultats de l'analyse.</p>
                <!-- Contenu des résultats à ajouter -->
            </div>
        </section>
    </main>
</template>


<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue';

</script>