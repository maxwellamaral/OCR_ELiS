<template>
  <div class="flex flex-col gap-6 p-6 rounded-xl bg-dark-card shadow-subtle border border-dark-border">
    <h2 class="text-dark-text text-[22px] font-bold leading-tight tracking-[-0.015em] pb-3 border-b border-dark-border">2. Resultados e Revisão</h2>
    <div class="flex flex-col gap-6">
      <div class="flex flex-col gap-4">
        <label class="text-base font-medium text-dark-text-soft" for="ocr-result">Resultado do OCR</label>
        <input class="w-full p-3 rounded-lg border border-dark-border bg-dark-bg text-dark-text focus:ring-2 focus:ring-dark-primary focus:border-dark-primary transition placeholder:text-dark-text-soft" id="ocr-result" readonly type="text" :value="ocrResult" />
      </div>
      <!-- Manual correction part is optional and not implemented in this version -->
    </div>
    <div v-if="detailedAnalysis.length > 0" class="py-3">
      <h3 class="text-lg font-semibold text-dark-text mb-4 border-b border-dark-border pb-2">Análise Detalhada dos Sinais</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
        <div v-for="(item, index) in detailedAnalysis" :key="index" class="flex flex-col items-center gap-2">
          <div class="w-full h-32 rounded-lg flex items-center justify-center sign-illustration bg-dark-bg">
            <img :src="item.image_base64" alt="Diagrama do Sinal" class="p-4 w-full h-full object-contain" />
          </div>
          <span class="text-base text-dark-text-soft font-medium text-center">Sinal {{ index + 1 }}: '{{ item.character }}'</span>
          <span class="text-base text-dark-text-soft font-medium text-center">Código Unicode: U+{{ item.character.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0') }}</span>
        </div>
      </div>
    </div>
    <!-- <div v-if="videoSrc" class="py-3"> -->
    <div class="py-3">
      <h3 class="text-lg font-semibold text-dark-text mb-4 border-b border-dark-border pb-2">Vídeo da Sequência</h3>
      <video controls class="w-full h-auto rounded-lg">
        <source :src="videoSrc" type="video/mp4">
        Seu navegador não suporta o elemento de vídeo.
      </video>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OcrResults',
  props: {
    ocrResult: String,
    detailedAnalysis: Array,
    videoSrc: String,
  },
};
</script>

<style scoped>
.sign-illustration {
  border: 1px solid #333333; /* dark-border */
}
</style>
