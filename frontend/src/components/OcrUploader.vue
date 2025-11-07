<template>
  <div class="flex flex-col gap-6 p-6 rounded-xl bg-dark-card shadow-subtle border border-dark-border">
    <h2 class="text-dark-text text-[22px] font-bold leading-tight tracking-[-0.015em] pb-3 border-b border-dark-border">1. Imagem para Análise</h2>
    <div
      @dragover.prevent
      @dragenter.prevent
      @drop.prevent="handleDrop"
      @click="openFileDialog"
      class="flex flex-col items-center gap-6 rounded-lg border-2 border-dashed border-dark-border px-6 py-10 bg-dark-bg cursor-pointer">
      <div class="flex max-w-[480px] flex-col items-center gap-2">
        <span class="material-symbols-outlined text-5xl text-dark-primary mb-2">upload_file</span>
        <p class="text-dark-text text-lg font-bold leading-tight tracking-[-0.015em] max-w-[480px] text-center">Arraste e solte uma imagem aqui, ou clique para selecionar</p>
        <p class="text-dark-text-soft text-sm font-normal leading-normal max-w-[480px] text-center">Imagens com 5 a 10 caracteres horizontais.</p>
      </div>
      <button class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-dark-primary text-dark-bg text-sm font-bold leading-normal tracking-[0.015em] hover:bg-opacity-90 transition-all shadow-md">
        <span class="truncate">Upload</span>
      </button>
      <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept="image/*" />
    </div>
    <div v-if="imagePreview" class="flex w-full justify-center">
      <div class="w-full max-w-2xl bg-black rounded-lg p-2 flex items-center justify-center border border-dark-border">
        <img class="rounded-md object-cover w-full h-auto" :src="imagePreview" alt="Pré-visualização da imagem enviada"/>
      </div>
    </div>
    <div class="flex px-4 py-3 justify-center">
      <button @click="$emit('perform-ocr')" class="flex min-w-[84px] w-full max-w-sm cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 bg-dark-secondary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-opacity-90 transition-all shadow-md gap-2">
        <span class="material-symbols-outlined">psychology</span>
        <span class="truncate">Realizar OCR</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OcrUploader',
  props: {
    imagePreview: String,
  },
  methods: {
    openFileDialog() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.$emit('image-uploaded', file);
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file) {
        this.$emit('image-uploaded', file);
      }
    },
  },
};
</script>
