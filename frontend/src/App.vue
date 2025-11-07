<template>
    <div class="font-display bg-dark-bg text-dark-text min-h-screen flex flex-col">
        <div class="layout-container flex h-full grow flex-col">
            <div class="px-4 sm:px-8 md:px-12 lg:px-16 flex flex-1 justify-center py-5">
                <div class="layout-content-container flex flex-col max-w-screen-xl w-full flex-1 gap-8">
                    <header
                        class="flex items-center justify-between whitespace-nowrap border-b border-solid border-dark-border px-6 py-4 rounded-xl bg-dark-card shadow-subtle">
                        <div class="flex items-center gap-4 text-dark-text">
                            <div class="size-6 text-dark-primary">
                                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="M44 11.2727C44 14.0109 39.8386 16.3957 33.69 17.6364C39.8386 18.877 44 21.2618 44 24C44 26.7382 39.8386 29.123 33.69 30.3636C39.8386 31.6043 44 33.9891 44 36.7273C44 40.7439 35.0457 44 24 44C12.9543 44 4 40.7439 4 36.7273C4 33.9891 8.16144 31.6043 14.31 30.3636C8.16144 29.123 4 26.7382 4 24C4 21.2618 8.16144 18.877 14.31 17.6364C8.16144 16.3957 4 14.0109 4 11.2727C4 7.25611 12.9543 4 24 4C35.0457 4 44 7.25611 44 11.2727Z"
                                        fill="currentColor"></path>
                                </svg>
                            </div>
                            <h1 class="text-dark-text text-xl font-bold leading-tight tracking-tight">ELiS -
                                Reconhecimento OCR</h1>
                        </div>
                        <div class="flex flex-1 justify-end gap-8">
                            <div class="flex items-center gap-9"><a
                                    class="text-dark-text-soft text-sm font-medium leading-normal hover:text-dark-primary transition-colors"
                                    href="#">About</a></div>
                        </div>
                    </header>
                    <main class="flex flex-col gap-8">
                        <div class="flex flex-wrap justify-between items-center gap-4 p-4">
                            <div class="flex flex-col gap-2">
                                <p class="text-dark-text text-4xl font-bold leading-tight tracking-tighter">Libras Sign
                                    Writing OCR</p>
                                <p class="text-dark-text-soft text-base font-normal leading-normal">Carregue uma imagem
                                    para análise e revisão educacional.</p>
                            </div>
                        </div>
                        <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
                            <OcrUploader @image-uploaded="handleImageUpload" @perform-ocr="performOcr"
                                :image-preview="imagePreview" />
                            <OcrResults :ocr-result="ocrResult" :detailed-analysis="detailedAnalysis"
                                :advanced-info="advancedInfo" />
                        </div>
                    </main>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import OcrUploader from './components/OcrUploader.vue';
import OcrResults from './components/OcrResults.vue';
import axios from 'axios';

export default {
    name: 'App',
    components: {
        OcrUploader,
        OcrResults,
    },
    data() {
        return {
            uploadedFile: null,
            imagePreview: null,
            ocrResult: '',
            detailedAnalysis: [],
            advancedInfo: {},
        };
    },
    methods: {
        handleImageUpload(file) {
            this.uploadedFile = file;
            this.imagePreview = URL.createObjectURL(file);
        },
        async performOcr() {
            if (!this.uploadedFile) {
                alert('Please upload an image first.');
                return;
            }

            const formData = new FormData();
            formData.append('image', this.uploadedFile);

            try {
                const response = await axios.post('http://127.0.0.1:5000/api/predict', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                this.ocrResult = response.data.recognized_text;
                this.detailedAnalysis = Array.isArray(response.data.detailed_analysis) ? response.data.detailed_analysis : [];
                this.advancedInfo = response.data.advanced_info || {};
            } catch (error) {
                console.error('Error performing OCR:', error);
                alert('An error occurred while performing OCR.');
            }
        },
    },
};
</script>

<style>
/* Using CDN for Tailwind, so no custom CSS needed here unless for specific overrides */
</style>
