document.addEventListener('DOMContentLoaded', function() {
    // Configuration des animations
    const animations = {
        DndMeme: {
            frameCount: 32,
            baseUrl: '/static/img/DndMeme/frame_',
            delay: '0.06s'
        },
        D20: {
            frameCount: 49,
            baseUrl: '/static/img/D20/frame_',
            delay: '0.06s'
        }
    };

    // Fonction pour précharger une image
    function preloadImage(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(url);
            img.onerror = () => reject(url);
            img.src = url;
        });
    }

    // Fonction pour formater le numéro de frame
    function formatFrameNumber(num) {
        return num.toString().padStart(2, '0');
    }

    // Préchargement par lots
    async function preloadAnimationFrames(animConfig, batchSize = 5) {
        const batches = [];
        const urls = [];

        // Créer les URLs pour toutes les frames
        for (let i = 0; i < animConfig.frameCount; i++) {
            const url = `${animConfig.baseUrl}${formatFrameNumber(i)}_delay-${animConfig.delay}.gif`;
            urls.push(url);
        }

        // Diviser en lots
        for (let i = 0; i < urls.length; i += batchSize) {
            batches.push(urls.slice(i, i + batchSize));
        }

        // Charger les lots séquentiellement
        for (const batch of batches) {
            await Promise.allSettled(batch.map(url => preloadImage(url)));
            // Petite pause entre les lots pour ne pas surcharger
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    // Démarrer le préchargement avec un délai pour ne pas bloquer le chargement initial
    setTimeout(() => {
        Object.values(animations).forEach(animConfig => {
            preloadAnimationFrames(animConfig).catch(console.error);
        });
    }, 1000);
}); 